from typing import List, Dict

from scrapers.base import RawJob
from scrapers.normalizer import normalize_raw_job
from scrapers.timesjobs_scraper import fetch_timesjobs
from scrapers.remoteok_scraper import fetch_remoteok
from scrapers.remotive_scraper import fetch_remotive


def fetch_all_sources(query: str, max_jobs_per_source: int = 20) -> List[Dict]:
    raw_jobs: List[RawJob] = []

    # Each source isolated so one failure doesn't kill all.
    sources = [
        ("timesjobs", fetch_timesjobs),
        ("remoteok", fetch_remoteok),
        ("remotive", fetch_remotive),
    ]

    for name, func in sources:
        try:
            print(f"Scraping {name}...")
            jobs = func(query=query, max_jobs=max_jobs_per_source)
            print(f"  > Found {len(jobs)} jobs")
            raw_jobs.extend(jobs)
        except Exception as e:
            print(f"[SCRAPER ERROR] {name}: {e}")

    normalized: List[Dict] = []
    for job in raw_jobs:
        try:
            normalized.append(normalize_raw_job(job))
        except Exception as e:
            print(f"[NORMALIZER ERROR] {job.source}: {e}")
            continue

    return normalized
