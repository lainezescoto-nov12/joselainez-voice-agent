"""Gmail API wrapper, used for appointment confirmation/reschedule emails."""
import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from app import config
from app.integrations.google_auth import get_credentials


def _service():
    return build("gmail", "v1", credentials=get_credentials(), cache_discovery=False)


def send_email(to: str, subject: str, body_text: str) -> dict:
    message = MIMEText(body_text)
    message["to"] = to
    message["from"] = config.DEALERSHIP_FROM_EMAIL or "me"
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return _service().users().messages().send(userId="me", body={"raw": raw}).execute()
