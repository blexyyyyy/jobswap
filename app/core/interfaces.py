from typing import List, Dict, Any, Protocol, Optional
from dataclasses import dataclass

@dataclass
class JobResult:
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    skills: List[str]
    raw_text: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

class JobSource(Protocol):
    """Interface for job scrapers."""
    def fetch_jobs(self, query: str, limit: int = 10) -> List[JobResult]:
        ...

class MatchScorer(Protocol):
    """Interface for ML scoring algorithms."""
    def score(self, user_profile: Dict[str, Any], job_data: Dict[str, Any]) -> float:
        ...

class ExplanationGenerator(Protocol):
    """Interface for LLM-based explanation generation."""
    def generate(self, user_profile: Dict[str, Any], job_summary: Dict[str, Any]) -> str:
        ...
