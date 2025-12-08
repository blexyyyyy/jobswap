from typing import List
import requests

from scrapers.base import RawJob, clean_text


API_URL = "https://remotive.com/api/remote-jobs"


def fetch_remotive(query: str, max_jobs: int = 20) -> List[RawJob]:
    try:
        resp = requests.get(API_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error fetching Remotive: {e}")
        return []

    jobs_raw = data.get("jobs", [])
    jobs: List[RawJob] = []

    for item in jobs_raw:
        title = clean_text(item.get("title"))
        if query.lower() not in (title or "").lower():
            continue

        company = clean_text(item.get("company_name"))
        url = item.get("url") or ""
        location = clean_text(item.get("candidate_required_location") or "Remote")
        description = clean_text(item.get("description") or "")

        tags = item.get("tags") or []
        skills = [t for t in tags if isinstance(t, str)]

        jobs.append(
            RawJob(
                title=title,
                company=company or "Unknown",
                location=location,
                skills=skills,
                description=description,
                url=url,
                raw_text=description,
                source="remotive",
            )
        )

        if len(jobs) >= max_jobs:
            break

    return jobs
