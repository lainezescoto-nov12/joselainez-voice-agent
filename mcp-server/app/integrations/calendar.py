"""Google Calendar wrapper used by the appointment tools."""
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build

from app import config
from app.integrations.google_auth import get_credentials


def _service():
    return build("calendar", "v3", credentials=get_credentials(), cache_discovery=False)


def list_busy_windows(start: datetime, end: datetime) -> list[dict]:
    """Return busy [start, end) windows on the service calendar between start/end."""
    body = {
        "timeMin": start.isoformat(),
        "timeMax": end.isoformat(),
        "items": [{"id": config.SERVICE_CALENDAR_ID}],
    }
    result = _service().freebusy().query(body=body).execute()
    return result["calendars"][config.SERVICE_CALENDAR_ID]["busy"]


def find_open_slots(day: datetime, slot_minutes: Optional[int] = None) -> list[dict]:
    """Return open appointment slots within business hours for the given day."""
    tz = ZoneInfo(config.BUSINESS_TIMEZONE)
    slot_minutes = slot_minutes or config.APPOINTMENT_SLOT_MINUTES

    # A naive `day` (e.g. from a date-only "YYYY-MM-DD" string) names a
    # calendar date, not a UTC instant — astimezone() would otherwise treat
    # it as system-local (UTC on Cloud Run) and shift it a day backward in
    # any timezone behind UTC.
    day_local = day.replace(tzinfo=tz) if day.tzinfo is None else day.astimezone(tz)
    window_start = day_local.replace(
        hour=config.BUSINESS_HOURS_START, minute=0, second=0, microsecond=0
    )
    window_end = day_local.replace(
        hour=config.BUSINESS_HOURS_END, minute=0, second=0, microsecond=0
    )

    busy = list_busy_windows(window_start, window_end)
    busy_ranges = [
        (datetime.fromisoformat(b["start"]), datetime.fromisoformat(b["end"]))
        for b in busy
    ]

    slots = []
    cursor = window_start
    delta = timedelta(minutes=slot_minutes)
    while cursor + delta <= window_end:
        slot_end = cursor + delta
        overlaps = any(cursor < b_end and slot_end > b_start for b_start, b_end in busy_ranges)
        if not overlaps:
            slots.append({"start": cursor.isoformat(), "end": slot_end.isoformat()})
        cursor = slot_end

    return slots


def create_event(
    summary: str,
    start: datetime,
    end: datetime,
    description: str = "",
    attendee_email: Optional[str] = None,
    extended_properties: Optional[dict] = None,
) -> dict:
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": config.BUSINESS_TIMEZONE},
        "end": {"dateTime": end.isoformat(), "timeZone": config.BUSINESS_TIMEZONE},
    }
    if attendee_email:
        event["attendees"] = [{"email": attendee_email}]
    if extended_properties:
        event["extendedProperties"] = {"private": extended_properties}

    return (
        _service()
        .events()
        .insert(calendarId=config.SERVICE_CALENDAR_ID, body=event, sendUpdates="none")
        .execute()
    )


def update_event(event_id: str, start: datetime, end: datetime) -> dict:
    patch = {
        "start": {"dateTime": start.isoformat(), "timeZone": config.BUSINESS_TIMEZONE},
        "end": {"dateTime": end.isoformat(), "timeZone": config.BUSINESS_TIMEZONE},
    }
    return (
        _service()
        .events()
        .patch(calendarId=config.SERVICE_CALENDAR_ID, eventId=event_id, body=patch)
        .execute()
    )


def delete_event(event_id: str) -> None:
    _service().events().delete(
        calendarId=config.SERVICE_CALENDAR_ID, eventId=event_id, sendUpdates="none"
    ).execute()


def get_event(event_id: str) -> dict:
    return (
        _service()
        .events()
        .get(calendarId=config.SERVICE_CALENDAR_ID, eventId=event_id)
        .execute()
    )
