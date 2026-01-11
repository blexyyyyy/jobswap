from app.core.interfaces import JobResult

# Alias for backward compatibility, but JobResult is the standard
RawJob = JobResult


def clean_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(str(value).split())
