from typing import List
import requests

from scrapers.base import RawJob, clean_text


API_URL = "https://remoteok.com/api"


def fetch_remoteok(query: str, max_jobs: int = 20) -> List[RawJob]:
    try:
        resp = requests.get(API_URL, timeout=15, headers={"User-Agent": "JobSwipe/1.0"}) # RemoteOK requires UA often
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error fetching RemoteOK: {e}")
        return []

    if not isinstance(data, list):
        return []

    jobs: List[RawJob] = []

    for item in data[1:]:  # first item is metadata
        title = clean_text(item.get("position") or item.get("title"))
        if query.lower() not in (title or "").lower():
            continue

        company = clean_text(item.get("company"))
        url = item.get("url") or item.get("apply_url") or ""
        location = clean_text(item.get("location") or "Remote")

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
                source="remoteok",
            )
        )

        if len(jobs) >= max_jobs:
            break

    return jobs
