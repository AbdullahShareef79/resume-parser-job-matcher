from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
import shutil
import os
from backend.resume_parser import parse_resume
from backend.job_matcher import rank_jobs

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve the HTML page from the frontend folder
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("D:/UNI TRIER FILES/My Projects/CV Parser/resume-parser-job-matcher/frontend/index.html", "r") as file:
        return HTMLResponse(content=file.read())

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
        # **1. Save the uploaded file**
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # **2. Parse the resume**
        parsed_data = parse_resume(file_path)

        # **3. Handle empty skills list**
        skills_list = parsed_data.get("skills", [])
        resume_skills_text = " ".join(skills_list) if skills_list else ""

        # **4. Rank jobs based on resume skills**
        ranked_jobs = rank_jobs(resume_skills_text, JOB_LISTINGS) if resume_skills_text else []

        # Print parsed data and ranked jobs for debugging purposes
        print("Parsed Data:", parsed_data)
        print("Ranked Jobs:", ranked_jobs)

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
