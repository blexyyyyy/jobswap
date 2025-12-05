from core.llm_client import JobPosting, extract_job_structured


def parse_job_text(raw_text: str) -> JobPosting:
    """
    Thin wrapper around the LLM job parser.

    Input: raw job posting text
    Output: JobPosting Pydantic model
    """
    return extract_job_structured(raw_text)