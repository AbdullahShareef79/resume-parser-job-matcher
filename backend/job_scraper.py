import requests
import logging
import time
import random
import json
import os
from typing import List, Dict, Any, Optional
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cache directory for storing results to reduce API calls during development
CACHE_DIR = "job_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# API options and endpoints
# 1. USAJobs API (requires registration but is free and legal to use): https://developer.usajobs.gov/
# 2. GitHub Jobs API (public data): https://jobs.github.com/api
# 3. Adzuna API (requires free API key): https://developer.adzuna.com/

# For this example, we'll use a combination of approaches:
# 1. Using a free job board API that allows access
# 2. Using RSS feeds from job boards that offer them
# 3. Implementing a fallback to a small sample of mock data to ensure the app works

# Sample API key placeholder - you would need to register for actual APIs
# Replace these with your actual API keys when you register
USA_JOBS_HOST = "data.usajobs.gov"
USA_JOBS_API_KEY = "YOUR_API_KEY_AFTER_REGISTRATION"  # Get from https://developer.usajobs.gov/
USA_JOBS_EMAIL = "your-email@example.com"

# For demo/testing, we'll include mock data to guarantee functionality
MOCK_JOB_DATA = {
    "python": [
        {
            "id": "py001",
            "title": "Senior Python Developer",
            "company": "TechCorp Inc.",
            "location": "San Francisco, CA (Remote)",
            "description": "Looking for an experienced Python developer to work on backend systems. Skills required: Python, Django, Flask, SQL, API development.",
            "url": "https://example.com/jobs/py001",
            "source_skill": "python"
        },
        {
            "id": "py002",
            "title": "Data Engineer - Python",
            "company": "Data Insights",
            "location": "New York, NY",
            "description": "Building data pipelines using Python, Pandas, and cloud technologies. Experience with AWS and big data processing required.",
            "url": "https://example.com/jobs/py002",
            "source_skill": "python"
        }
    ],
    "javascript": [
        {
            "id": "js001",
            "title": "Frontend Developer",
            "company": "WebWorks",
            "location": "Remote",
            "description": "Creating responsive UI components using React and modern JavaScript. Knowledge of TypeScript and state management is a plus.",
            "url": "https://example.com/jobs/js001",
            "source_skill": "javascript"
        }
    ],
    "data science": [
        {
            "id": "ds001",
            "title": "Data Scientist",
            "company": "Analytics Pro",
            "location": "Boston, MA",
            "description": "Applying machine learning models to business problems. Required skills: Python, R, SQL, Tableau, and experience with deep learning frameworks.",
            "url": "https://example.com/jobs/ds001",
            "source_skill": "data science"
        }
    ]
}

def get_jobs_from_usa_jobs(skill: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch jobs from USAJobs.gov API based on a skill.
    
    Args:
        skill (str): Skill to search for
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of job dictionaries
    """
    # Check if we have cached results first
    cache_file = os.path.join(CACHE_DIR, f"usajobs_{skill.replace(' ', '_')}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                logger.info(f"Using cached data for {skill} from USA Jobs")
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading cache file: {e}")
    
    # If no API key is provided or we're in demo mode, return empty list
    if USA_JOBS_API_KEY == "YOUR_API_KEY_AFTER_REGISTRATION":
        logger.warning("No USA Jobs API key provided - skipping actual API call")
        return []
        
    headers = {
        "Host": USA_JOBS_HOST,
        "User-Agent": USA_JOBS_EMAIL,
        "Authorization-Key": USA_JOBS_API_KEY
    }
    
    params = {
        "Keyword": skill,
        "ResultsPerPage": max_results,
        "Fields": "min"
    }
    
    try:
        response = requests.get(
            "https://data.usajobs.gov/api/Search", 
            headers=headers, 
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        jobs = []
        for job in data.get("SearchResult", {}).get("SearchResultItems", []):
            position = job.get("MatchedObjectDescriptor", {})
            
            jobs.append({
                "id": position.get("PositionID", str(uuid.uuid4())),
                "title": position.get("PositionTitle", "No Title"),
                "company": position.get("OrganizationName", "U.S. Government"),
                "location": position.get("PositionLocationDisplay", "Multiple Locations"),
                "description": position.get("QualificationSummary", "No description available."),
                "url": position.get("PositionURI", "https://www.usajobs.gov/"),
                "source_skill": skill
            })
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(jobs, f)
            
        return jobs
    except Exception as e:
        logger.error(f"Error fetching from USA Jobs API: {e}")
        return []

def get_jobs_from_github_jobs(skill: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch jobs from GitHub Jobs API based on a skill.
    Note: GitHub Jobs API was deprecated, so this is for demonstration purposes.
    
    Args:
        skill (str): Skill to search for
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of job dictionaries
    """
    cache_file = os.path.join(CACHE_DIR, f"github_{skill.replace(' ', '_')}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                logger.info(f"Using cached data for {skill} from GitHub Jobs")
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading cache file: {e}")
    
    # This API is deprecated but the format is useful for demonstration
    try:
        response = requests.get(
            f"https://jobs.github.com/positions.json?description={skill}",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        jobs = []
        for job in data[:max_results]:
            jobs.append({
                "id": job.get("id", str(uuid.uuid4())),
                "title": job.get("title", "No Title"),
                "company": job.get("company", "Unknown Company"),
                "location": job.get("location", "Unknown Location"),
                "description": job.get("description", "No description available."),
                "url": job.get("url", "https://jobs.github.com/"),
                "source_skill": skill
            })
        
        # Cache the results
        with open(cache_file, 'w') as f:
            json.dump(jobs, f)
            
        return jobs
    except Exception as e:
        logger.error(f"Error fetching from GitHub Jobs API: {e}")
        return []

def get_mock_jobs(skill: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Get mock job data when APIs are unavailable.
    
    Args:
        skill (str): Skill to search for
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of job dictionaries
    """
    skill_lower = skill.lower()
    
    # Get jobs for the specific skill or use a default category
    if skill_lower in MOCK_JOB_DATA:
        jobs = MOCK_JOB_DATA[skill_lower]
    else:
        # Create some dynamic fake data
        random_titles = [
            f"{skill.title()} Developer", 
            f"Senior {skill.title()} Engineer",
            f"{skill.title()} Specialist",
            f"{skill.title()} Analyst",
            f"{skill.title()} Consultant"
        ]
        
        companies = ["TechCorp", "Innovative Solutions", "Digital Systems", "NextGen Tech", "CodeMasters"]
        locations = ["Remote", "New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA"]
        
        jobs = []
        for i in range(min(max_results, 5)):
            jobs.append({
                "id": f"{skill_lower[:3]}{i:03d}",
                "title": random_titles[i % len(random_titles)],
                "company": companies[i % len(companies)],
                "location": locations[i % len(locations)],
                "description": f"We're seeking a skilled professional with expertise in {skill}. "
                               f"Join our team and work on exciting projects using cutting-edge technology.",
                "url": f"https://example.com/jobs/{skill_lower.replace(' ', '-')}-{i+1}",
                "source_skill": skill
            })
    
    return jobs[:max_results]

def fetch_jobs(skills: List[str], max_results_per_skill: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch job listings based on extracted resume skills using a combination of sources.

    Args:
        skills (list): List of skills extracted from the resume.
        max_results_per_skill (int): Maximum number of results per skill.

    Returns:
        list: A list of job dictionaries containing title, company, location, and description.
    """
    job_listings = []
    
    # Deduplicate skills while preserving order
    unique_skills = list(dict.fromkeys([skill.strip().lower() for skill in skills if skill.strip()]))
    logger.info(f"Searching jobs for skills: {', '.join(unique_skills)}")
    
    for skill in unique_skills:
        # Try USA Jobs API first (if configured)
        usa_jobs = get_jobs_from_usa_jobs(skill, max_results_per_skill)
        if usa_jobs:
            job_listings.extend(usa_jobs)
            logger.info(f"Found {len(usa_jobs)} jobs from USA Jobs for '{skill}'")
        
        # Try GitHub Jobs API (demonstration only)
        github_jobs = get_jobs_from_github_jobs(skill, max_results_per_skill)
        if github_jobs:
            job_listings.extend(github_jobs)
            logger.info(f"Found {len(github_jobs)} jobs from GitHub Jobs for '{skill}'")
        
        # If no jobs found from APIs, use mock data
        if not usa_jobs and not github_jobs:
            mock_jobs = get_mock_jobs(skill, max_results_per_skill)
            job_listings.extend(mock_jobs)
            logger.info(f"Using {len(mock_jobs)} mock jobs for '{skill}'")
            
        # Add a small delay between API calls
        time.sleep(random.uniform(0.5, 1.5))
    
    # Deduplicate job listings
    seen = set()
    unique_jobs = []
    
    for job in job_listings:
        # Create a key from the title and company to detect duplicates
        key = (job.get("title", ""), job.get("company", ""))
        if key not in seen:
            seen.add(key)
            
            # Add a match score for compatibility with job_matcher.py
            job["match_score"] = random.uniform(70.0, 95.0)
            # Add a posted date
            job["posted_date"] = f"{random.randint(1, 28)} days ago"
            
            unique_jobs.append(job)
    
    logger.info(f"Total unique jobs found: {len(unique_jobs)}")
    return unique_jobs


if __name__ == "__main__":
    test_skills = ["Python", "Data Science", "JavaScript"]
    results = fetch_jobs(test_skills, max_results_per_skill=3)

    # Print results
    if results:
        print(f"Total jobs fetched: {len(results)}")
        for idx, job in enumerate(results):
            print(f"\nJob {idx+1}:")
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"Match score: {job['match_score']:.1f}%")
            print(f"Source skill: {job['source_skill']}")
    else:
        print("No jobs found.")