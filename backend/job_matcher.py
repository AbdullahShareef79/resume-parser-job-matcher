from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def calculate_similarity(resume_text, job_descriptions):
    resume_text = preprocess_text(resume_text)
    job_descriptions = [preprocess_text(job) for job in job_descriptions]
    all_texts = [resume_text] + job_descriptions
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    return similarity_scores

def rank_jobs(resume_text, job_listings):  
    job_descriptions = [job["description"] for job in job_listings]
    similarity_scores = calculate_similarity(resume_text, job_descriptions)
    for i, job in enumerate(job_listings):
        job["similarity_score"] = similarity_scores[i]
    return sorted(job_listings, key=lambda x: x["similarity_score"], reverse=True)