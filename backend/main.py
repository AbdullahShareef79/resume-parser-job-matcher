from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
import os
from resume_parser import parse_resume
from job_matcher import rank_jobs

app = FastAPI()

# Root route
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Resume Parser and Job Matcher API!"}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    {
        "title": "Web Developer",
        "company": "Web Solutions",
        "location": "Chicago, IL",
        "description": "We need a web developer proficient in React and Node.js.",
    },
]

@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # ... (existing code to save the file)

        # Parse the resume
        parsed_data = parse_resume(file_path)

        # Join the list of skills into a single string
        resume_skills_text = " ".join(parsed_data["skills"])  # <-- Fix here

        # Rank jobs based on the resume skills
        ranked_jobs = rank_jobs(resume_skills_text, JOB_LISTINGS)  # <-- Pass the string

        return {
            "filename": file.filename,
            "parsed_data": parsed_data,
            "matched_jobs": ranked_jobs,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)