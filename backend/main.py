from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

# Import resume parsing & job matching modules
from backend.resume_parser import parse_resume
from backend.job_matcher import rank_jobs
from backend.job_scraper import fetch_jobs # Ensure this function is properly implemented

# Initialize FastAPI app
app = FastAPI(
    title="Resume Parser and Job Matcher",
    description="A tool to parse resumes and match them with real job listings.",
    version="1.1.0",
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development only)
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Directory to store uploaded resumes
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve the HTML page from the frontend folder
@app.get("/", response_class=HTMLResponse)
async def read_root():
    try:
        with open("frontend/index.html", "r") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend index.html not found")


# Endpoint to upload and process a resume
@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Parse the resume
        parsed_data = parse_resume(file_path)
        if "error" in parsed_data:
            raise HTTPException(status_code=400, detail=parsed_data["error"])

        # Fetch job listings from the internet based on extracted skills
        job_listings = fetch_jobs(parsed_data["skills"])  # Uses real-time job search

        # Rank jobs based on resume skills
        ranked_jobs = rank_jobs(parsed_data["skills"], job_listings)

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
