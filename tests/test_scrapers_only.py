#!/usr/bin/env python
"""Test scrapers only - no API calls"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("SCRAPER-ONLY TEST (NO API CALLS)")
print("=" * 70)

# Test 1: Import scraper
print("\n[1/3] Importing scraper...")
try:
    from scrapers.timesjobs_scraper import fetch_timesjobs
    print("  ✓ Scraper imported successfully")
except ImportError as e:
    print(f"  ✗ Import error: {e}")
    sys.exit(1)

# Test 2: Run scraper with different queries
print("\n[2/3] Testing scraper with different queries...")
test_cases = [
    ("python developer", "Bangalore", 1),
    ("java developer", "Mumbai", 1),
    ("data scientist", None, 2),
]

for query, location, max_pages in test_cases:
    try:
        jobs = fetch_timesjobs(query, location=location, max_pages=max_pages)
        print(f"  ✓ Query: '{query}' | Location: {location or 'Any'} | Found: {len(jobs)} jobs")
        if jobs:
            print(f"    Sample: {jobs[0]['title']} @ {jobs[0]['company']}")
    except Exception as e:
        print(f"  ✗ Error for query '{query}': {e}")

# Test 3: Validate job structure
print("\n[3/3] Validating job data structure...")
try:
    jobs = fetch_timesjobs("test", max_pages=1)
    if jobs:
        required_fields = ['title', 'company', 'location', 'skills', 'summary', 'source_url']
        job = jobs[0]
        missing = [f for f in required_fields if f not in job]
        if missing:
            print(f"  ✗ Missing fields: {missing}")
        else:
            print("  ✓ All required fields present")
            for field in required_fields:
                value = job[field]
                print(f"    - {field}: {value[:50]}..." if len(str(value)) > 50 else f"    - {field}: {value}")
except Exception as e:
    print(f"  ✗ Validation error: {e}")

print("\n" + "=" * 70)
print("SCRAPER TEST COMPLETE!")
print("=" * 70)
