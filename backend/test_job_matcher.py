from job_matcher import rank_jobs

# Sample job listings
JOB_LISTINGS = [
    {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "New York, NY",
        "description": "We are looking for a software engineer with experience in Python and machine learning.",
    },
    {
        "title": "Data Scientist",
        "company": "Data Inc",
        "location": "San Francisco, CA",
        "description": "Join our team as a data scientist to work on cutting-edge AI projects.",
    },
]

# Sample resume skills
resume_skills = "Python, Machine Learning, NLP"

# Rank jobs
ranked_jobs = rank_jobs(resume_skills, JOB_LISTINGS)
print(ranked_jobs)