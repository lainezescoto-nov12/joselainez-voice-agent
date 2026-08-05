"""Per-phone-number rate limit for the public demo call, backed by Firestore
(same project as the MCP server, separate collection). OTP proves the
requester controls the number once; this caps how often that same number
can trigger a real call regardless -- the actual abuse brake.
"""
from datetime import datetime, timedelta, timezone

from google.cloud import firestore

from app import config

_client: firestore.Client | None = None


def _db() -> firestore.Client:
    global _client
    if _client is None:
        _client = firestore.Client(project=config.GCP_PROJECT_ID)
    return _client


def check_and_record(phone_number: str) -> tuple[bool, str | None]:
    """Returns (allowed, reason_if_blocked)."""
    doc_ref = _db().collection("demo_call_log").document(phone_number)
    doc = doc_ref.get()

    now = datetime.now(timezone.utc)
    if doc.exists:
        last_called_at = doc.to_dict().get("last_called_at")
        if last_called_at is not None:
            elapsed = now - last_called_at
            if elapsed < timedelta(hours=config.RATE_LIMIT_HOURS):
                remaining = timedelta(hours=config.RATE_LIMIT_HOURS) - elapsed
                hours_left = max(1, int(remaining.total_seconds() // 3600))
                return False, f"This number already used the demo recently — try again in about {hours_left} hour(s)."

    doc_ref.set({"last_called_at": now})
    return True, None
