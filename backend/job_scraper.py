import requests
from bs4 import BeautifulSoup
import time
import random
import concurrent.futures
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# More realistic and diverse user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

INDEED_BASE_URL = "https://www.indeed.com/jobs?q={}&start={}"

def get_session():
    """
    Create a session with retry capabilities and random user agent.
    
    Returns:
        requests.Session: Configured session object
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set a random user agent
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    return session

def fetch_page(url, skill, page_num):
    """
    Fetch a single page of job listings.
    
    Args:
        url (str): The URL to fetch
        skill (str): The skill being searched
        page_num (int): The page number
        
    Returns:
        list: Job listings from this page
    """
    page_jobs = []
    session = get_session()
    
    try:
        logger.info(f"Fetching jobs for: {skill} (Page {page_num})")
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("div", class_="job_seen_beacon")
        
        for job in job_cards:
            try:
                title_elem = job.find("h2", class_="jobTitle")
                company_elem = job.find("span", class_="companyName")
                location_elem = job.find("div", class_="companyLocation")
                description_elem = job.find("div", class_="job-snippet")
                
                if title_elem and company_elem and location_elem:
                    page_jobs.append({
                        "title": title_elem.text.strip(),
                        "company": company_elem.text.strip(),
                        "location": location_elem.text.strip(),
                        "description": description_elem.text.strip() if description_elem else "No description available.",
                        "source_skill": skill,
                        "page": page_num
                    })
            except AttributeError as e:
                logger.warning(f"Error parsing job card: {e}")
                continue
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
    
    # Randomized sleep to avoid detection
    time.sleep(random.uniform(2, 5))
    return page_jobs

def fetch_jobs(skills, max_pages=2):
    """
    Fetch job listings from Indeed based on extracted resume skills.

    Args:
        skills (list): List of skills extracted from the resume.
        max_pages (int): Number of pages to scrape (default: 2).

    Returns:
        list: A list of job dictionaries containing title, company, location, and description.
    """
    job_listings = []
    all_tasks = []
    
    # Deduplicate skills while preserving order
    unique_skills = list(dict.fromkeys([skill.strip().lower() for skill in skills if skill.strip()]))
    
    # Create a pool of workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for skill in unique_skills:
            skill_query = "+".join(skill.split())  # Format skill for URL
            for page_num in range(max_pages):
                page_offset = page_num * 10  # Indeed uses increments of 10
                url = INDEED_BASE_URL.format(skill_query, page_offset)
                
                # Submit task to thread pool
                task = executor.submit(fetch_page, url, skill, page_num + 1)
                all_tasks.append(task)
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(all_tasks):
            try:
                page_results = future.result()
                if page_results:
                    job_listings.extend(page_results)
                    logger.info(f"Fetched {len(page_results)} jobs from a page")
            except Exception as e:
                logger.error(f"Error in worker thread: {e}")
    
    # Deduplicate job listings
    seen = set()
    unique_jobs = []
    
    for job in job_listings:
        # Create a key from the title and company to detect duplicates
        key = (job["title"], job["company"])
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    logger.info(f"Total unique jobs found: {len(unique_jobs)}")
    return unique_jobs