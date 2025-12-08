from typing import List
import requests
from bs4 import BeautifulSoup

from scrapers.base import RawJob, clean_text


BASE_URL = "https://www.timesjobs.com/candidate/job-search.html"


def fetch_timesjobs(query: str, max_jobs: int = 20) -> List[RawJob]:
    params = {
        "searchType": "personalizedSearch",
        "from": "submit",
        "txtKeywords": query,
        "txtLocation": "India",
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching TimesJobs: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select(".job-bx")  # you may tweak this

    jobs: List[RawJob] = []

    for card in cards[:max_jobs]:
        title_el = card.select_one("h2 a")
        company_el = card.select_one(".joblist-comp-name")
        loc_el = card.select_one(".sjw.dp8 span")

        title = clean_text(title_el.get_text()) if title_el else ""
        company = clean_text(company_el.get_text()) if company_el else ""
        location = clean_text(loc_el.get_text()) if loc_el else "India"
        url = title_el["href"] if title_el and title_el.has_attr("href") else ""

        desc_el = card.select_one(".list-job-dtl")
        desc = clean_text(desc_el.get_text()) if desc_el else ""

        jobs.append(
            RawJob(
                title=title,
                company=company,
                location=location,
                skills=[],  # we let normalizer infer if needed
                description=desc,
                url=url,
                raw_text=desc,
                source="timesjobs",
            )
        )

    return jobs