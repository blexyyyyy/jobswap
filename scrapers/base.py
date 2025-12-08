from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RawJob:
    title: str
    company: str
    location: str
    skills: List[str]
    description: str
    url: str
    raw_text: str
    source: str


def clean_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(str(value).split())
