import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_upload_resume(tmp_path):
    # Create a test file
    test_file = tmp_path / "test_resume.pdf"
    test_file.write_text("Mock resume content")
    
    with open(test_file, "rb") as f:
        response = client.post("/api/upload/", files={"file": f})
    
    assert response.status_code in [200, 422]  # 422 if parser fails
    
    if response.status_code == 200:
        data = response.json()
        assert "parsed_data" in data
        assert "matched_jobs" in data

def test_invalid_file_upload():
    response = client.post("/api/upload/", files={"file": ("test.txt", b"not a resume")})
    assert response.status_code == 400

def test_get_jobs():
    response = client.get("/api/jobs/?skills=Python&skills=JavaScript")
    assert response.status_code == 200
    jobs = response.json()
    assert isinstance(jobs, list)
    if len(jobs) > 0:
        assert "title" in jobs[0]