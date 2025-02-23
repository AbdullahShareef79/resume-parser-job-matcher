import requests
from bs4 import BeautifulSoup
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

INDEED_BASE_URL = "https://www.indeed.com/jobs?q={}&start={}"

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
    
    for skill in skills:
        skill_query = "+".join(skill.split())  # Format skill for URL
        for page in range(0, max_pages * 10, 10):  # Indeed uses increments of 10
            url = INDEED_BASE_URL.format(skill_query, page)
            print(f"Fetching jobs for: {skill} (Page {page // 10 + 1})")

            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(f"Failed to fetch jobs for {skill}. Status Code:", response.status_code)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("div", class_="job_seen_beacon")

            for job in job_cards:
                title = job.find("h2", class_="jobTitle")
                company = job.find("span", class_="companyName")
                location = job.find("div", class_="companyLocation")
                description = job.find("div", class_="job-snippet")

                if title and company and location:
                    job_listings.append({
                        "title": title.text.strip(),
                        "company": company.text.strip(),
                        "location": location.text.strip(),
                        "description": description.text.strip() if description else "No description available.",
                    })

            time.sleep(random.uniform(1, 3))  # Prevent rate-limiting

    return job_listings
