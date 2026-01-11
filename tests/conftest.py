import sys
import asyncio
import pytest
from app.core.logging import logger

# Fix for Windows Asyncio Loop
@pytest.fixture(scope="session", autouse=True)
def fix_windows_event_loop():
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Note: pytest-asyncio usually provides its own event_loop fixture, 
# but if we need a custom one or scope override:
@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for each test case.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

def pytest_configure(config):
    """Configuration for pytest."""
    # Ensure our logger doesn't spam stdout during tests unless we want it
    logger.setLevel("WARNING") 
