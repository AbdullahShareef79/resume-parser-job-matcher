import pytest
from job_matcher import rank_jobs, calculate_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

@pytest.fixture
def sample_data():
    return {
        "resume_text": "Experienced Python developer with machine learning skills and AWS experience.",
        "resume_skills": ["Python", "Machine Learning", "AWS"],
        "jobs": [
            {
                "title": "Python Developer",
                "description": "Looking for Python developer with AWS experience",
                "required_skills": ["Python", "AWS"]
            },
            {
                "title": "Java Developer",
                "description": "Need Java expert with Spring framework",
                "required_skills": ["Java", "Spring"]
            },
            {
                "title": "Data Scientist",
                "description": "Machine learning expert needed",
                "required_skills": ["Machine Learning", "Python"]
            }
        ]
    }

def test_calculate_similarity(sample_data):
    job_descriptions = [job["description"] for job in sample_data["jobs"]]
    scores = calculate_similarity(sample_data["resume_text"], job_descriptions)
    
    assert len(scores) == len(job_descriptions)
    assert scores[0] > scores[1]  # Python job should score higher than Java
    assert scores[2] > scores[1]  # Data science job should score higher than Java

def test_rank_jobs(sample_data):
    ranked = rank_jobs(sample_data["resume_skills"], sample_data["jobs"])
    
    assert len(ranked) == len(sample_data["jobs"])
    assert all("match_percentage" in job for job in ranked)  # Verify field exists
    
    # Python Developer should rank highest (has 2 matching skills)
    python_dev = next(j for j in ranked if j["title"] == "Python Developer")
    data_scientist = next(j for j in ranked if j["title"] == "Data Scientist")
    java_dev = next(j for j in ranked if j["title"] == "Java Developer")
    
    assert python_dev["match_percentage"] > java_dev["match_percentage"]
    assert data_scientist["match_percentage"] > java_dev["match_percentage"]