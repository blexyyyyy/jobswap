import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM


def send_email_with_attachment(
    to_email: str,
    subject: str,
    body: str,
    resume_path: Optional[str] = None,
):
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD]):
        # Fallback for dev: log it
        print(f"[MOCK EMAIL] To: {to_email}")
        print(f"[MOCK EMAIL] Subject: {subject}")
        if resume_path:
            print(f"[MOCK EMAIL] Attachment: {resume_path}")
        return

    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if resume_path:
        file_path = Path(resume_path)
        if file_path.exists():
            with file_path.open("rb") as f:
                data = f.read()
            msg.add_attachment(
                data,
                maintype="application",
                subtype="octet-stream",
                filename=file_path.name,
            )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"SMTP Error: {e}")
        raise e
