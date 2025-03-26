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
    # Startup tasks
    logger.info("Application starting up...")
    # Here you could initialize DB connections, load ML models, etc.
    yield
    # Shutdown tasks
    logger.info("Application shutting down...")
    # Here you could close DB connections, save state, etc.

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Resume Parser and Job Matcher",
    description="A tool to parse resumes and match them with job listings",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",  # Separate API docs from frontend
    redoc_url="/api/redoc",
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add request processing time middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

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
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (5MB max)
    file.file.seek(0, 2)  # Move to end of file
    file_size = file.file.tell()  # Get file size
    file.file.seek(0)  # Reset file pointer
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB."
        )

# Function to clean up old files
async def cleanup_old_files(age_hours: int = 24):
    """Remove files older than specified hours"""
    now = time.time()
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        # If file is older than age_hours, delete it
        if os.path.isfile(file_path) and os.stat(file_path).st_mtime < now - age_hours * 3600:
            try:
                os.remove(file_path)
                logger.info(f"Removed old file: {filename}")
            except Exception as e:
                logger.error(f"Error removing {filename}: {e}")

# Endpoint to upload and process a resume
@app.post("/api/upload/", response_model=ResumeResponse)
async def upload_resume(file: UploadFile = File(...)):
        try:
            # Validate file type
            if file.content_type not in ["application/pdf", 
                                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    "application/rtf"]:
                raise HTTPException(status_code=400, detail="Invalid file type")

            # Create uploads directory if not exists
            os.makedirs("uploads", exist_ok=True)
            
            # Generate unique filename
            file_ext = os.path.splitext(file.filename)[1]
            file_path = f"uploads/{uuid.uuid4()}{file_ext}"
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Parse resume
            parsed_data = parse_resume(file_path)
            
            # Fetch and rank jobs
            job_listings = fetch_jobs(parsed_data.get("skills", []))
            ranked_jobs = rank_jobs(parsed_data.get("skills", []), job_listings)
            
            return {
                "id": str(uuid.uuid4()),
                "filename": file.filename,
                "upload_date": datetime.now().isoformat(),
                "parsed_data": parsed_data,
                "matched_jobs": ranked_jobs
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
# Endpoint to get processed resume data by ID
@app.get("/api/resume/{resume_id}", response_model=Optional[ResumeResponse])
async def get_resume(resume_id: str):
    # In a real app, you would fetch from a database
    # For this example, we'll return a not found error since we don't have persistence
    raise HTTPException(status_code=404, detail="Resume not found")

# Endpoint to get job listings without uploading a resume
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

# For backward compatibility with original code
@app.post("/upload/")
async def upload_resume_legacy(file: UploadFile = File(...)):
    """Legacy endpoint for compatibility with original code"""
    # Redirect to the new endpoint
    response = await upload_resume(BackgroundTasks(), file)
    return JSONResponse(
        status_code=200,
        content={
            "filename": response["filename"],
            "parsed_data": response["parsed_data"],
            "matched_jobs": response["matched_jobs"],
        },
    )

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)