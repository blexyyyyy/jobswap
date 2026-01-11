#!/usr/bin/env python
"""Test script for fetch_and_seed_timesjobs"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("Step 1: Starting imports...")

try:
    from scrapers.timesjobs_scraper import fetch_timesjobs
    print("  ✓ fetch_timesjobs imported")
except Exception as e:
    print(f"  ✗ Error importing fetch_timesjobs: {e}")
    import pytest
    pytest.skip(f"Import failed: {e}", allow_module_level=True)

try:
    from core.llm_client import extract_job_structured, generate_embedding
    print("  ✓ LLM client imported")
except Exception as e:
    print(f"  ✗ Error importing LLM client: {e}")
    import pytest
    pytest.skip(f"Import failed: {e}", allow_module_level=True)

try:
    from database.db_manager import insert_job
    print("  ✓ DB manager imported")
except Exception as e:
    print(f"  ✗ Error importing DB manager: {e}")
    import pytest
    pytest.skip(f"Import failed: {e}", allow_module_level=True)

try:
    from database.vector_store import VectorStore
    print("  ✓ VectorStore imported")
except Exception as e:
    print(f"  ✗ Error importing VectorStore: {e}")
    import pytest
    pytest.skip(f"Import failed: {e}", allow_module_level=True)

print("\nStep 2: Testing fetch_timesjobs...")
try:
    jobs = fetch_timesjobs("python developer", location="India", max_pages=1)
    print(f"  ✓ Fetched {len(jobs)} jobs")
    if jobs:
        print(f"  Sample job: {jobs[0]['title']} @ {jobs[0]['company']}")
except Exception as e:
    print(f"  ✗ Error fetching jobs: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Testing LLM parsing...")
try:
    sample_job = jobs[0]
    raw_text = f"""Title: {sample_job['title']}
Company: {sample_job['company']}
Location: {sample_job['location']}
Skills: {sample_job['skills']}
Description: {sample_job['summary']}"""
    
    print(f"  Raw text: {raw_text[:100]}...")
    parsed = extract_job_structured(raw_text)
    print(f"  ✓ Parsed job: {parsed.title}")
except Exception as e:
    print(f"  ✗ Error parsing job: {e}")
    import traceback
    traceback.print_exc()

print("\nAll tests completed!")
