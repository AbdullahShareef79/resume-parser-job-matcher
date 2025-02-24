from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
import re
import numpy as np
import logging
from concurrent.futures import ThreadPoolExecutor
import os
import pickle
import nltk
from collections import Counter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize NLTK resources with error handling
def initialize_nltk():
    """Initialize NLTK resources with proper error handling."""
    nltk_resources = ["stopwords", "punkt", "wordnet", "averaged_perceptron_tagger"]
    
    for resource in nltk_resources:
        try:
            nltk.download(resource, quiet=True)
            logger.info(f"Successfully loaded NLTK resource: {resource}")
        except Exception as e:
            logger.error(f"Failed to download NLTK resource {resource}: {e}")
            
    # Return resources for use
    try:
        stop_words = set(stopwords.words("english"))
        lemmatizer = WordNetLemmatizer()
        stemmer = PorterStemmer()
        return stop_words, lemmatizer, stemmer
    except Exception as e:
        logger.error(f"Error initializing NLTK tools: {e}")
        # Fallback to empty set if resources fail to load
        return set(), None, None

# Initialize NLTK resources
stop_words, lemmatizer, stemmer = initialize_nltk()

# Additional domain-specific stop words for job matching
JOB_STOP_WORDS = {
    "job", "work", "position", "opportunity", "role", "candidate", "applicant",
    "company", "team", "required", "requirement", "qualification", "experience",
    "responsibility", "duties", "skill", "ability", "looking", "seeking", 
    "hiring", "employ", "please", "email", "contact", "apply", "click",
    "submit", "resume", "cv", "year", "day", "month", "week", "hour", "time"
}

# Domain keywords with higher importance
DOMAIN_KEYWORDS = {
    "software": 1.5, "developer": 1.5, "engineer": 1.5, "programmer": 1.5,
    "analyst": 1.5, "manager": 1.5, "specialist": 1.5, "architect": 1.5,
    "data": 1.5, "science": 1.5, "scientist": 1.5, "machine": 1.5, "learning": 1.5,
    "ai": 1.5, "artificial": 1.5, "intelligence": 1.5, "web": 1.5, "mobile": 1.5,
    "frontend": 1.5, "backend": 1.5, "fullstack": 1.5, "cloud": 1.5, "devops": 1.5,
    "security": 1.5, "network": 1.5, "database": 1.5, "design": 1.5, "ux": 1.5, "ui": 1.5,
    "product": 1.5, "project": 1.5, "agile": 1.5, "scrum": 1.5, "marketing": 1.5,
    "financial": 1.5, "healthcare": 1.5, "education": 1.5, "retail": 1.5
}

def get_vectorizer_cache_path():
    """Return a path for caching the vectorizer model."""
    cache_dir = os.path.join(os.path.expanduser("~"), ".job_ranking_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "tfidf_vectorizer.pkl")

def save_vectorizer(vectorizer):
    """Save the trained vectorizer for reuse."""
    try:
        with open(get_vectorizer_cache_path(), 'wb') as f:
            pickle.dump(vectorizer, f)
        logger.info("TF-IDF vectorizer cached successfully")
    except Exception as e:
        logger.warning(f"Failed to cache vectorizer: {e}")

def load_vectorizer():
    """Load a previously trained vectorizer if available."""
    try:
        cache_path = get_vectorizer_cache_path()
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                vectorizer = pickle.load(f)
            logger.info("Loaded cached TF-IDF vectorizer")
            return vectorizer
    except Exception as e:
        logger.warning(f"Failed to load cached vectorizer: {e}")
    return None

def preprocess_text(text, use_stemming=False):
    """
    Cleans and preprocesses text for better similarity matching.
    
    Args:
        text (str): The text to preprocess
        use_stemming (bool): Whether to use stemming in addition to lemmatization
        
    Returns:
        str: Preprocessed text
    """
    if not text or not isinstance(text, str):
        return ""

    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers
    text = re.sub(r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '', text)
    
    # Remove special characters but keep hyphens for compound words
    text = re.sub(r'[^\w\s-]', '', text)
    
    # Replace hyphens with spaces to split compound words
    text = re.sub(r'-', ' ', text)
    
    # Tokenize text
    try:
        words = word_tokenize(text)
    except:
        # Fallback to simple splitting if tokenization fails
        words = text.split()
    
    # Combine NLTK stopwords with domain-specific ones
    all_stop_words = stop_words.union(JOB_STOP_WORDS)
    
    # Apply lemmatization and remove stopwords
    processed_words = []
    for word in words:
        if word not in all_stop_words and len(word) > 1:
            try:
                if lemmatizer:
                    word = lemmatizer.lemmatize(word)
                if use_stemming and stemmer:
                    word = stemmer.stem(word)
                processed_words.append(word)
            except Exception as e:
                logger.warning(f"Error processing word '{word}': {e}")
                # Add the original word if processing fails
                if word not in all_stop_words:
                    processed_words.append(word)
    
    return " ".join(processed_words)

def extract_key_phrases(text, n=2):
    """
    Extract important n-grams from text.
    
    Args:
        text (str): The text to analyze
        n (int): Maximum n-gram size
        
    Returns:
        str: Text with added key phrases
    """
    if not text:
        return ""
    
    # Preprocess text first
    processed_text = preprocess_text(text)
    tokens = processed_text.split()
    
    # Generate n-grams
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngrams.append(" ".join(tokens[i:i+n]))
    
    # Add the most frequent n-grams back to the text
    if ngrams:
        # Count n-gram frequency
        ngram_counts = Counter(ngrams)
        # Get the top 10 n-grams
        top_ngrams = [ng for ng, _ in ngram_counts.most_common(10)]
        # Append them to the processed text
        return processed_text + " " + " ".join(top_ngrams)
    
    return processed_text

def extract_skills_from_text(text, skills_db):
    """
    Extract skills mentioned in text based on a skills database.
    
    Args:
        text (str): The text to analyze
        skills_db (set): Set of skill terms to match
        
    Returns:
        set: Set of skills found in the text
    """
    if not text or not skills_db:
        return set()
    
    # Normalize text
    text = text.lower()
    
    # Extract skills
    found_skills = set()
    for skill in skills_db:
        skill_lower = skill.lower()
        # Check for whole word matches to avoid partial matches
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', text):
            found_skills.add(skill)
    
    return found_skills

def calculate_similarity(resume_text, job_descriptions, resume_skills=None, dim_reduction=True):
    """
    Computes similarity scores between the resume and job descriptions using advanced techniques.
    
    Args:
        resume_text (str): The preprocessed resume text
        job_descriptions (list): List of job description texts
        resume_skills (set): Optional set of skills extracted from the resume
        dim_reduction (bool): Whether to use dimensionality reduction
        
    Returns:
        list: Similarity scores for each job
    """
    if not job_descriptions:
        return []

    # Preprocess resume text with key phrase extraction
    processed_resume = extract_key_phrases(resume_text)
    
    # Process all job descriptions in parallel
    with ThreadPoolExecutor(max_workers=min(10, len(job_descriptions))) as executor:
        processed_jobs = list(executor.map(extract_key_phrases, job_descriptions))
    
    # Create and prepare vectorizer
    vectorizer = load_vectorizer()
    
    if not vectorizer:
        # Configuration for a more robust TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            analyzer='word',
            min_df=0.01,  # Ignore terms that appear in less than 1% of documents
            max_df=0.95,  # Ignore terms that appear in more than 95% of documents
            sublinear_tf=True,  # Apply sublinear tf scaling (1 + log(tf))
            use_idf=True,
            ngram_range=(1, 2),  # Include both unigrams and bigrams
            max_features=5000  # Limit features to reduce noise
        )
        
    # Create pipeline with optional dimensionality reduction
    if dim_reduction:
        n_components = min(100, len(job_descriptions) + 1 - 1)  # Adjust for small datasets
        pipeline = Pipeline([
            ('tfidf', vectorizer),
            ('svd', TruncatedSVD(n_components=max(2, n_components)))  # Ensure at least 2 components
        ])
        all_texts = [processed_resume] + processed_jobs
        try:
            # Transform texts using the pipeline
            tfidf_matrix = pipeline.fit_transform(all_texts)
            # Cache the vectorizer for future use
            save_vectorizer(pipeline.named_steps['tfidf'])
        except Exception as e:
            logger.error(f"Error in dimensionality reduction: {e}")
            # Fallback to basic TF-IDF without reduction
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            save_vectorizer(vectorizer)
    else:
        # Use TF-IDF without dimensionality reduction
        all_texts = [processed_resume] + processed_jobs
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        save_vectorizer(vectorizer)
    
    # Compute cosine similarity
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Enhance scores with skills matching if skills are provided
    if resume_skills:
        # Process each job to extract skills
        for i, job_text in enumerate(job_descriptions):
            if i >= len(similarity_scores):
                break
                
            # Extract skills from job description
            job_skills = extract_skills_from_text(job_text, resume_skills)
            
            # Calculate skill match ratio (number of matching skills / number of resume skills)
            if resume_skills:
                skill_match_ratio = len(job_skills) / len(resume_skills) if resume_skills else 0
                
                # Boost similarity score based on skill matches (weighted 30%)
                similarity_scores[i] = (similarity_scores[i] * 0.7) + (skill_match_ratio * 0.3)
    
    # Normalize scores to [0,1] for better comparison
    if np.max(similarity_scores) > 0:
        similarity_scores = similarity_scores / np.max(similarity_scores)
    
    return similarity_scores

def rank_jobs(resume_text, job_listings, resume_skills=None):
    """
    Ranks jobs based on similarity scores with additional metadata.
    
    Args:
        resume_text (str): The resume text
        job_listings (list): List of job dictionaries
        resume_skills (set): Optional set of skills extracted from the resume
        
    Returns:
        list: Ranked job listings with similarity scores and match details
    """
    if not job_listings:
        logger.warning("No job listings provided for ranking")
        return []

    # Preprocess resume text
    processed_resume_text = preprocess_text(resume_text)
    
    # Extract job descriptions
    job_descriptions = []
    for job in job_listings:
        description = job.get("description", "")
        if not description:
            description = " ".join([
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", "")
            ])
        job_descriptions.append(description)
    
    try:
        # Calculate similarity scores
        similarity_scores = calculate_similarity(
            processed_resume_text, 
            job_descriptions,
            resume_skills
        )
        
        # Add similarity scores and match details to job listings
        ranked_jobs = []
        for i, job in enumerate(job_listings):
            if i < len(similarity_scores):
                # Create a copy of the job to avoid modifying the original
                job_copy = job.copy()
                
                # Add similarity score
                job_copy["similarity_score"] = float(similarity_scores[i])
                
                # Add match confidence level
                if similarity_scores[i] >= 0.8:
                    job_copy["match_level"] = "Excellent"
                elif similarity_scores[i] >= 0.6:
                    job_copy["match_level"] = "Good"
                elif similarity_scores[i] >= 0.4:
                    job_copy["match_level"] = "Fair"
                else:
                    job_copy["match_level"] = "Low"
                    
                # Extract matching skills if resume_skills is provided
                if resume_skills and "description" in job:
                    matching_skills = extract_skills_from_text(job["description"], resume_skills)
                    job_copy["matching_skills"] = list(matching_skills)
                    job_copy["skill_match_count"] = len(matching_skills)
                    job_copy["skill_match_ratio"] = len(matching_skills) / len(resume_skills) if resume_skills else 0
                
                ranked_jobs.append(job_copy)
        
        # Sort jobs by similarity score in descending order
        ranked_jobs.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        logger.info(f"Successfully ranked {len(ranked_jobs)} jobs")
        return ranked_jobs
        
    except Exception as e:
        logger.error(f"Error during job ranking: {e}")
        # Return original listings if ranking fails
        return job_listings

def calculate_job_match_statistics(ranked_jobs):
    """
    Calculate statistics about job matches.
    
    Args:
        ranked_jobs (list): List of ranked job dictionaries
        
    Returns:
        dict: Statistics about job matches
    """
    if not ranked_jobs:
        return {
            "total_jobs": 0,
            "average_score": 0,
            "top_match_score": 0,
            "excellent_matches": 0,
            "good_matches": 0,
            "fair_matches": 0,
            "low_matches": 0
        }
    
    # Calculate statistics
    scores = [job.get("similarity_score", 0) for job in ranked_jobs]
    excellent = sum(1 for job in ranked_jobs if job.get("match_level") == "Excellent")
    good = sum(1 for job in ranked_jobs if job.get("match_level") == "Good")
    fair = sum(1 for job in ranked_jobs if job.get("match_level") == "Fair")
    low = sum(1 for job in ranked_jobs if job.get("match_level") == "Low")
    
    return {
        "total_jobs": len(ranked_jobs),
        "average_score": sum(scores) / len(scores) if scores else 0,
        "top_match_score": max(scores) if scores else 0,
        "excellent_matches": excellent,
        "good_matches": good,
        "fair_matches": fair,
        "low_matches": low
    }

def get_top_job_recommendations(ranked_jobs, top_n=5, min_score=0.4):
    """
    Get top job recommendations above a minimum score.
    
    Args:
        ranked_jobs (list): List of ranked job dictionaries
        top_n (int): Number of top jobs to return
        min_score (float): Minimum similarity score threshold
        
    Returns:
        list: Top job recommendations
    """
    if not ranked_jobs:
        return []
    
    # Filter jobs by minimum score
    qualified_jobs = [job for job in ranked_jobs if job.get("similarity_score", 0) >= min_score]
    
    # Return top N jobs
    return qualified_jobs[:top_n]


if __name__ == "__main__":
    # Sample resume text
    resume_text = """
    Experienced software engineer with expertise in Python, machine learning, and web development. 
    Strong background in AI, data science, and cloud computing. Proficient in building scalable applications.
    """

    # Sample job descriptions
    job_descriptions = [
        "Looking for a software engineer skilled in Python, AI, and cloud computing. Experience with machine learning is a plus.",
        "Hiring a web developer proficient in JavaScript, React, and Node.js. Experience with frontend frameworks required.",
        "Seeking a data scientist with strong skills in machine learning, statistics, and data visualization.",
        "We need a DevOps engineer with expertise in CI/CD, cloud platforms, and container orchestration."
    ]

    # Run the similarity function
    similarity_scores = calculate_similarity(resume_text, job_descriptions)

    # Print results
    print("\nJob Similarity Scores:")
    for i, score in enumerate(similarity_scores):
        print(f"Job {i+1}: {score:.4f}")
