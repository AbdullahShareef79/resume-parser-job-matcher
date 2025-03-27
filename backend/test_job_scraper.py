import pytest
from job_scraper import fetch_jobs, get_mock_jobs

def test_get_mock_jobs():
    jobs = get_mock_jobs("Python")
    assert len(jobs) > 0
    assert all("Python" in job["title"] or "python" in job["description"].lower() for job in jobs)
    
    jobs = get_mock_jobs("Nonexistent Skill")
    assert len(jobs) > 0  # Should still return generic jobs

def test_fetch_jobs():
    # Test with mock data only
    jobs = fetch_jobs(["Python", "JavaScript"])
    assert len(jobs) > 0
    
    # Verify structure
    required_keys = {"title", "company", "location", "description", "url"}
    for job in jobs:
        assert all(key in job for key in required_keys)
    
    # Test with empty skills
    assert len(fetch_jobs([])) == 0