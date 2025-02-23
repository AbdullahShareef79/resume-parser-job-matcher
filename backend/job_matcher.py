from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re
import numpy as np

# Ensure stopwords and tokenizer resources are available
import nltk
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

def preprocess_text(text):
    """Cleans and preprocesses text for better similarity matching."""
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    words = word_tokenize(text)  # Tokenize text
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]  # Lemmatization & stopword removal
    return " ".join(words)

def calculate_similarity(resume_text, job_descriptions):
    """Computes similarity scores between the resume and job descriptions."""
    if not job_descriptions:
        return []

    resume_text = preprocess_text(resume_text)
    job_descriptions = [preprocess_text(job) for job in job_descriptions]

    # Vectorization with TF-IDF
    vectorizer = TfidfVectorizer()
    all_texts = [resume_text] + job_descriptions
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Compute cosine similarity
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Normalize scores to [0,1] for better comparison
    if np.max(similarity_scores) > 0:
        similarity_scores = similarity_scores / np.max(similarity_scores)

    return similarity_scores

def rank_jobs(resume_text, job_listings):
    """Ranks jobs based on similarity scores."""
    if not job_listings:
        return []

    job_descriptions = [job.get("description", "") for job in job_listings]
    similarity_scores = calculate_similarity(resume_text, job_descriptions)

    for i, job in enumerate(job_listings):
        job["similarity_score"] = similarity_scores[i] if i < len(similarity_scores) else 0.0

    return sorted(job_listings, key=lambda x: x["similarity_score"], reverse=True)
