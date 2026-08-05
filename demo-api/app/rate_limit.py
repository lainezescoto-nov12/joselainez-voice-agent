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


def check(phone_number: str) -> tuple[bool, str | None]:
    """Returns (allowed, reason_if_blocked). Read-only -- does not record a use.

    Recording happens separately, via record(), and only once the call this
    check is gating has actually succeeded. Recording here unconditionally
    would burn a caller's rate-limit window on a call that never went
    through (e.g. an ElevenLabs/Twilio failure downstream of this check).
    """
    doc = _db().collection("demo_call_log").document(phone_number).get()
    if not doc.exists:
        return True, None

    last_called_at = doc.to_dict().get("last_called_at")
    if last_called_at is None:
        return True, None

    elapsed = datetime.now(timezone.utc) - last_called_at
    if elapsed < timedelta(hours=config.RATE_LIMIT_HOURS):
        remaining = timedelta(hours=config.RATE_LIMIT_HOURS) - elapsed
        hours_left = max(1, int(remaining.total_seconds() // 3600))
        return False, f"This number already used the demo recently — try again in about {hours_left} hour(s)."
    return True, None


def record(phone_number: str) -> None:
    """Record a successful call, starting this number's rate-limit window."""
    _db().collection("demo_call_log").document(phone_number).set(
        {"last_called_at": datetime.now(timezone.utc)}
    )
