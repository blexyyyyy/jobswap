from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.logging import logger
import requests

def log_attempt_number(retry_state):
    """return the result of the last call attempt"""
    logger.warning(f"Retrying: {retry_state.attempt_number}...")

# Standard retry policy for external APIs
retry_external_api = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.RequestException, TimeoutError)),
    before_sleep=log_attempt_number,
    reraise=True
)

def safe_execute(func, default=None, *args, **kwargs):
    """Safely execute a function and return default on failure."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Execution failed for {func.__name__}: {e}")
        return default
