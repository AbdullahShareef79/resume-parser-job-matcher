from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

# Initialize FastAPI app
app = FastAPI(
    title="Resume Parser and Job Matcher",
    description="A tool to parse resumes and match them with job listings.",
    version="1.0.0",
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development only)
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Serve static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Directory to store uploaded resumes
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve the HTML page from the frontend folder
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("frontend/index.html", "r") as file:
        return HTMLResponse(content=file.read())

# Sample job listings (can be replaced with a database or external API)
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

# Endpoint to upload and process a resume
@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # **1. Save the uploaded file**
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer);

        # **2. Parse the resume**
        parsed_data = {
            "name": "John Doe",
            "skills": ["Python", "Machine Learning", "FastAPI"],
            "experience": "5 years",
        }  # Replace with actual parsing logic

        # **3. Rank jobs based on resume skills**
        ranked_jobs = JOB_LISTINGS  # Replace with actual ranking logic

        # Return the response
        return JSONResponse(
            status_code=200,
            content={
                "filename": file.filename,
                "parsed_data": parsed_data,
                "matched_jobs": ranked_jobs,
            },
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)