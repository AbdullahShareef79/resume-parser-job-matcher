from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import shutil
import os
import uuid
import logging
from datetime import datetime
import time
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
import mimetypes

# Import resume parsing & job matching modules
from backend.resume_parser import parse_resume
from backend.job_matcher import rank_jobs
from backend.job_scraper import fetch_jobs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Directory configuration
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".rtf"}

# Pydantic models for request/response validation
class JobListing(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    match_score: float
    posted_date: Optional[str] = None

class ParsedResume(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    
class ResumeResponse(BaseModel):
    id: str
    filename: str
    upload_date: str
    parsed_data: ParsedResume
    matched_jobs: List[JobListing] = Field(default_factory=list)

# Lifecycle event handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Resume Parser and Job Matcher",
    description="A tool to parse resumes and match them with job listings",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files with cache control
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Serve the HTML page from the frontend folder
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("frontend/index.html", "r") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        logger.error("Frontend index.html not found")
        raise HTTPException(status_code=404, detail="Frontend index.html not found")

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file type and size"""
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB."
        )

# Cleanup function
async def cleanup_old_files(age_hours: int = 24):
    now = time.time()
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path) and os.stat(file_path).st_mtime < now - age_hours * 3600:
            try:
                os.remove(file_path)
                logger.info(f"Removed old file: {filename}")
            except Exception as e:
                logger.error(f"Error removing {filename}: {e}")

# Main upload endpoint
@app.post("/api/upload/", response_model=ResumeResponse)
async def upload_resume(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        validate_file(file)
        
        original_filename = file.filename
        file_ext = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {original_filename} -> {unique_filename}")
        
        background_tasks.add_task(cleanup_old_files)
        
        parsed_data = parse_resume(file_path)
        if isinstance(parsed_data, dict) and "error" in parsed_data:
            raise HTTPException(status_code=400, detail=parsed_data["error"])

        parsed_data.setdefault("skills", [])

        job_listings = fetch_jobs(parsed_data.get("skills", []))
        ranked_jobs = rank_jobs(parsed_data.get("skills", []), job_listings)

        response_data = {
            "id": str(uuid.uuid4()),
            "filename": original_filename,
            "upload_date": datetime.now().isoformat(),
            "parsed_data": parsed_data,
            "matched_jobs": ranked_jobs
        }
        
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing resume: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your resume")

# Get job listings without uploading a resume
@app.get("/api/jobs/")
async def get_jobs(skills: Optional[List[str]] = Query(None), limit: int = Query(10, ge=1, le=50)):
    try:
        if not skills or len(skills) == 0:
            raise HTTPException(status_code=400, detail="At least one skill must be provided")
        
        job_listings = fetch_jobs(skills)
        ranked_jobs = rank_jobs(skills, job_listings)
        
        return ranked_jobs[:limit]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching job listings")

# **FIXED Legacy Upload Endpoint**
@app.post("/upload/")
async def upload_resume_legacy(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Legacy endpoint for compatibility with older frontend requests"""
    response = await upload_resume(background_tasks, file)
    return JSONResponse(
        status_code=200,
        content={
            "filename": response.filename,
            "parsed_data": response.parsed_data.dict(),
            "matched_jobs": [job.dict() for job in response.matched_jobs],
        },
    )

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
