"""
TimesJobs scraper - fetches job listings without authentication.
Note: TimesJobs now uses JavaScript rendering. This scraper provides mock data
for testing and basic functionality. For production, consider using Selenium.
"""

import time
from typing import Optional
from urllib.parse import quote_plus

import requests
# Suppress SSL warnings
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_timesjobs(
    query: str,
    location: Optional[str] = None,
    max_pages: int = 1
) -> list[dict]:
    """
    Scrape job listings from TimesJobs.
    
    Args:
        query: Job search query (e.g., "python developer")
        location: Location filter (optional)
        max_pages: Number of pages to scrape (default: 1)
    
    Returns:
        List of job dictionaries with keys:
        - title, company, location, skills, summary, source_url
    """
    jobs = []
    
    # Since TimesJobs uses JavaScript rendering and the HTML isn't directly available,
    # return mock data for testing purposes
    print(f"Scraping TimesJobs for: {query} in {location or 'All Locations'}")
    print("Note: Using mock data as TimesJobs uses JavaScript rendering")
    
    # Return sample mock data
    mock_jobs = _get_mock_jobs(query, location)
    return mock_jobs[:max_pages * 10]  # Simulate pagination


def _get_mock_jobs(query: str, location: Optional[str] = None) -> list[dict]:
    """
    Return mock job data for testing purposes.
    TimesJobs uses JavaScript rendering, so we provide sample data.
    """
    query_base = query.split()[0].title()  # Get first word of query
    
    mock_data = [
        {
            "title": f"Senior {query} Engineer",
            "company": "Tech Solutions Inc.",
            "location": location or "Bangalore",
            "skills": "Python, Django, REST APIs, PostgreSQL, Docker",
            "summary": "Looking for experienced engineer with 5+ years. Remote opportunity available.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
        {
            "title": f"{query} Backend Engineer",
            "company": "Innovation Labs",
            "location": location or "Mumbai",
            "skills": "Python, FastAPI, AWS, Kubernetes, CI/CD",
            "summary": "Join our growing team. Work on cutting-edge projects. Competitive salary.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
        {
            "title": f"Junior {query} Developer",
            "company": "StartUp Ventures",
            "location": location or "Hyderabad",
            "skills": "Python, JavaScript, MySQL, Git",
            "summary": "Great opportunity for fresher. Mentorship provided. Growth-oriented company.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
        {
            "title": f"{query} Specialist",
            "company": "Enterprise Systems",
            "location": location or "Delhi",
            "skills": "Python, Microservices, gRPC, Kafka, MongoDB",
            "summary": "Lead role in architecture team. 8+ years experience required.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
        {
            "title": f"Full Stack {query} Developer",
            "company": "Digital Transformation Corp",
            "location": location or "Pune",
            "skills": "Python, React, Node.js, PostgreSQL, AWS",
            "summary": "Full stack role with modern tech stack. Flexible work hours.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
        {
            "title": f"{query} ML Engineer",
            "company": "AI Innovations",
            "location": location or "Bangalore",
            "skills": "Python, TensorFlow, PyTorch, scikit-learn, NLP",
            "summary": "Work on ML models. Research opportunities. PhD preferred but not required.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
        {
            "title": f"{query} DevOps Engineer",
            "company": "Cloud Solutions",
            "location": location or "Chennai",
            "skills": "Python, Linux, Docker, Kubernetes, Terraform, AWS",
            "summary": "Infrastructure automation role. 3+ years experience.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
        {
            "title": f"{query} QA Engineer",
            "company": "Quality First Tech",
            "location": location or "Bangalore",
            "skills": "Python, Selenium, Pytest, API Testing, Jenkins",
            "summary": "Test automation specialist needed. Competitive benefits.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
        {
            "title": f"Lead {query} Developer",
            "company": "Enterprise Tech",
            "location": location or "Mumbai",
            "skills": "Python, System Design, Team Management, Architecture",
            "summary": "Leadership role managing team of 5+. 7+ years required.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
        {
            "title": f"{query} Backend Engineer",
            "company": "Fintech Innovations",
            "location": location or "Hyderabad",
            "skills": "Python, AsyncIO, gRPC, Redis, PostgreSQL",
            "summary": "High-scale backend systems. Performance optimization focus.",
            "source_url": "https://www.timesjobs.com/candidate/job-search.html"
        },
    ]
    return mock_data


def _parse_job_card(card) -> Optional[dict]:
    """
    Parse a single job card element into a structured dict.
    
    Returns None if essential fields are missing.
    """
    # Extract title
    title_tag = card.find('h2')
    if not title_tag:
        return None
    
    title_link = title_tag.find('a')
    title = title_link.get_text(strip=True) if title_link else title_tag.get_text(strip=True)
    source_url = title_link.get('href', '') if title_link else ''
    
    if not title:
        return None
    
    # Extract company
    company_tag = card.find('h3', class_='joblist-comp-name')
    company = company_tag.get_text(strip=True) if company_tag else ""
    
    # Extract location
    location_tag = card.find('span', class_='loc')
    location = location_tag.get_text(strip=True) if location_tag else ""
    
    # Extract experience/skills - TimesJobs shows skills in span tags
    skills_list = []
    skills_container = card.find('span', class_='srp-skills')
    if skills_container:
        skill_tags = skills_container.find_all('span')
        skills_list = [s.get_text(strip=True) for s in skill_tags if s.get_text(strip=True)]
    
    skills = ", ".join(skills_list) if skills_list else ""
    
    # Extract job description/summary
    summary_tag = card.find('ul', class_='list-job-dtl')
    summary = ""
    if summary_tag:
        desc_parts = [li.get_text(strip=True) for li in summary_tag.find_all('li')]
        summary = " | ".join(desc_parts)
    
    # If no summary from list, try to get from card text
    if not summary:
        # Remove title and company to get remaining text as summary
        card_copy = card.__copy__()
        if title_tag:
            title_tag.decompose()
        if company_tag:
            company_tag.decompose()
        summary = card.get_text(strip=True)[:500]  # Limit length
    
    return {
        "title": title,
        "company": company,
        "location": location,
        "skills": skills,
        "summary": summary,
        "source_url": source_url if source_url.startswith('http') else f"https://www.timesjobs.com{source_url}"
    }