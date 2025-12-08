from datetime import datetime
from typing import List, Dict, Tuple, Optional

from database.connection import get_db_connection
from app.core.config import AUTO_APPLY_MAX_PER_HOUR
from utils.email_client import send_email_with_attachment


def _user_sent_last_hour(conn, user_id: int) -> int:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) as cnt
        FROM auto_apply_queue
        WHERE user_id = ?
          AND status = 'sent'
          AND sent_at >= DATETIME('now', '-1 hour')
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    return row["cnt"] if row else 0


def queue_auto_apply(
    user: dict,
    job_ids: List[int],
    override_email: Optional[str] = None,
) -> Tuple[int, int, int]:
    """
    Returns (queued, already_queued, failed)
    """
    user_id = user["id"]
    queued = 0
    already = 0
    failed = 0

    with get_db_connection() as conn:
        cursor = conn.cursor()

        for job_id in job_ids:
            # Avoid duplicate queue entries for same job+user in pending state
            cursor.execute(
                """
                SELECT 1 FROM auto_apply_queue
                WHERE user_id = ? AND job_id = ? AND status = 'pending'
                """,
                (user_id, job_id),
            )
            if cursor.fetchone():
                already += 1
                continue

            # Get job info (for subject/body)
            cursor.execute(
                "SELECT title, company FROM jobs WHERE id = ?",
                (job_id,),
            )
            job = cursor.fetchone()
            if not job:
                failed += 1
                continue

            subject = f"Application for {job['title']} at {job['company']}"
            body = f"""Hello,

Please find my resume attached for the role "{job['title']}" at {job['company']}.

Best regards,
{user.get('name') or 'Candidate'}
"""
            # Logic for where to send email: override -> job table email (if exists) -> placeholder
            # ideally, jobs table should have 'apply_email' or source_url might contain it?
            # For now, rely on override or simulate.
            # If no override and we don't have job email, we fail (or we could queue with missing email/status='draft').
            # The prompt says: "use override_email field from the user. You decide later how to source emails."
            
            to_email = override_email or user.get("email") # Wait, user.get("email") is USER's email. We shouldn't send TO user.
            
            # Correction: The prompt code snippet said:
            # to_email = override_email or user.get("email")
            # But the logic comment above it says "fallback if no job/company email yet".
            # Sending to oneself is a safe fallback for testing!
            
            if not to_email:
                failed += 1
                continue

            # Store queue row
            cursor.execute(
                """
                INSERT INTO auto_apply_queue
                    (user_id, job_id, to_email, subject, body, resume_path, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    user_id,
                    job_id,
                    to_email,
                    subject,
                    body,
                    user.get("resume_file_path"),
                ),
            )
            queued += 1

        conn.commit()

    return queued, already, failed


def process_auto_apply_batch(limit: int = 10) -> Dict:
    """
    Sends up to `limit` pending emails while respecting per-hour limit.
    """
    processed = 0
    sent = 0
    failed = 0
    skipped_rate_limit = 0

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Fetch pending jobs ordered by created_at
        cursor.execute(
            """
            SELECT * FROM auto_apply_queue
            WHERE status = 'pending'
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        
        # We must commit updates inside the loop or after processing, 
        # but to update status individually we need careful transaction mgmt.
        # Since we are in a 'with conn', cursor context is shared.
        
        # Actually safer to process one by one in terms of Python logic, but batch fetch is okay.
        
        for row in rows:
            processed += 1
            user_id = row["user_id"]

            # Rate limiting per user
            sent_last_hour = _user_sent_last_hour(conn, user_id)
            if sent_last_hour >= AUTO_APPLY_MAX_PER_HOUR:
                skipped_rate_limit += 1
                continue

            try:
                send_email_with_attachment(
                    to_email=row["to_email"],
                    subject=row["subject"],
                    body=row["body"],
                    resume_path=row["resume_path"],
                )

                cursor.execute(
                    """
                    UPDATE auto_apply_queue
                    SET status = 'sent',
                        sent_at = CURRENT_TIMESTAMP,
                        error = NULL
                    WHERE id = ?
                    """,
                    (row["id"],),
                )
                sent += 1

            except Exception as e:
                failed += 1
                cursor.execute(
                    """
                    UPDATE auto_apply_queue
                    SET status = 'failed',
                        error = ?,
                        retry_count = retry_count + 1
                    WHERE id = ?
                    """,
                    (str(e), row["id"]),
                )

        conn.commit()

    return {
        "processed": processed,
        "sent": sent,
        "failed": failed,
        "skipped_rate_limit": skipped_rate_limit,
    }
