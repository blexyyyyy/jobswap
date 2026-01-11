"""
Fetch jobs from TimesJobs and seed database with embeddings.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("DEBUG: Script started", file=sys.stderr)
print("DEBUG: Importing modules...", file=sys.stderr)

from core.llm_client import extract_job_structured, generate_embedding
from database.db_manager import insert_job
from database.vector_store import VectorStore
from scrapers.timesjobs_scraper import fetch_timesjobs


def build_raw_text(job_dict: dict) -> str:
    """Convert scraped job dict into raw text for LLM parsing."""
    return f"""Title: {job_dict['title']}
Company: {job_dict['company']}
Location: {job_dict['location']}
Skills: {job_dict['skills']}
Description: {job_dict['summary']}"""


def build_embedding_text(parsed_job) -> str:
    """Build text for embedding generation."""
    # Combine key fields for semantic search
    try:
        if isinstance(parsed_job.skills, list):
            skills_text = ", ".join(parsed_job.skills)
        elif isinstance(parsed_job.skills, str):
            skills_text = parsed_job.skills
        else:
            skills_text = str(parsed_job.skills) if parsed_job.skills else ""
    except (TypeError, AttributeError):
        skills_text = ""
    
    return f"{parsed_job.title} {skills_text} {parsed_job.description}"


def create_job_signature(job_data: dict) -> str:
    """Create unique signature to avoid duplicates."""
    return f"{job_data['title'].lower()}|{job_data['company'].lower()}|{job_data['location'].lower()}"


def main():
    """Main seeding workflow."""
    print("=" * 60)
    print("TimesJobs Scraper & Seeder")
    print("=" * 60)
    
    # Initialize vector store once
    vector_store = VectorStore()
    
    # Define search queries
    queries = [
        ("python developer", None),
        ("data analyst", None),
        ("machine learning engineer", None),
        ("data scientist", "Bangalore"),
    ]
    
    # Track processed jobs to avoid duplicates
    processed_signatures = set()
    
    # Statistics
    stats = {
        "scraped": 0,
        "parsed": 0,
        "stored": 0,
        "skipped_duplicates": 0,
        "failed": 0
    }
    
    for query, location in queries:
        print(f"\n{'=' * 60}")
        print(f"Searching: {query}" + (f" in {location}" if location else ""))
        print("=" * 60)
        
        try:
            # Scrape jobs
            jobs = fetch_timesjobs(query=query, location=location, max_pages=2)
            stats["scraped"] += len(jobs)
            
            print(f"\nProcessing {len(jobs)} scraped jobs...")
            
            for idx, job_dict in enumerate(jobs, 1):
                try:
                    # Build raw text for LLM
                    raw_text = build_raw_text(job_dict)
                    
                    # Parse with LLM
                    print(f"\n[{idx}/{len(jobs)}] Parsing: {job_dict['title']} @ {job_dict['company']}")
                    parsed = extract_job_structured(raw_text)
                    stats["parsed"] += 1
                    
                    # Convert to job_data dict
                    job_data = {
                        "title": parsed.title,
                        "company": parsed.company,
                        "location": parsed.location,
                        "seniority": parsed.seniority,
                        "skills": ", ".join(parsed.skills) if parsed.skills else "",
                        "description": parsed.description,
                    }
                    
                    # Check for duplicates
                    signature = create_job_signature(job_data)
                    if signature in processed_signatures:
                        print(f"  [SKIP] Skipping duplicate")
                        stats["skipped_duplicates"] += 1
                        continue
                    
                    processed_signatures.add(signature)
                    
                    # Insert into database
                    job_id = insert_job(job_data, raw_text)
                    
                    if job_id is None:
                        print(f"  [FAIL] Failed to insert into database")
                        stats["failed"] += 1
                        continue
                    
                    print(f"  [OK] Inserted with ID: {job_id}")
                    
                    # Generate embedding
                    embedding_text = build_embedding_text(parsed)
                    embedding = generate_embedding(embedding_text)
                    
                    # Store in vector database
                    vector_store.add_jobs(
                        ids=[str(job_id)],
                        embeddings=[embedding],
                        metadatas=[{
                            "title": job_data["title"],
                            "company": job_data["company"],
                            "location": job_data["location"],
                            "seniority": job_data["seniority"],
                            "source": "timesjobs",
                            "source_url": job_dict.get("source_url", ""),
                        }]
                    )
                    
                    print(f"  [EMBED] Embedded and stored in vector DB")
                    stats["stored"] += 1
                    
                except Exception as e:
                    print(f"  [ERROR] Error processing job: {e}")
                    stats["failed"] += 1
                    continue
                    
        except Exception as e:
            print(f"\n[ERROR] Error processing query '{query}': {e}")
            continue
    
    # Print final statistics
    print("\n" + "=" * 60)
    print("FINAL STATISTICS")
    print("=" * 60)
    print(f"Jobs scraped:          {stats['scraped']}")
    print(f"Jobs parsed:           {stats['parsed']}")
    print(f"Jobs stored:           {stats['stored']}")
    print(f"Duplicates skipped:    {stats['skipped_duplicates']}")
    print(f"Failed:                {stats['failed']}")
    print("=" * 60)
    
    if stats["stored"] > 0:
        print(f"\n[SUCCESS] Successfully seeded {stats['stored']} jobs into database!")
    else:
        print(f"\n[WARNING] No jobs were stored. Check errors above.")


if __name__ == "__main__":
    main()