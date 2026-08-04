"""check_availability, book_appointment, reschedule_appointment, cancel_appointment."""
from datetime import datetime, timedelta

from app import config
from app.data import store
from app.integrations import calendar, gmail


def check_availability(date: str, tenant_id: str = config.DEFAULT_TENANT_ID) -> dict:
    """List open appointment slots on the given date (YYYY-MM-DD)."""
    day = datetime.fromisoformat(date)
    slots = calendar.find_open_slots(day)
    return {"tenant_id": tenant_id, "date": date, "open_slots": slots}


def book_appointment(
    customer_name: str,
    customer_email: str,
    start_time: str,
    reason: str,
    customer_phone: str = "",
    tenant_id: str = config.DEFAULT_TENANT_ID,
) -> dict:
    """Book an appointment. start_time is an ISO 8601 datetime, slot length from config.

    customer_phone is optional but recommended — it lets find_appointment
    locate this booking in a later call if the customer doesn't have their
    email handy on a callback.
    """
    start = datetime.fromisoformat(start_time)
    end = start + timedelta(minutes=config.APPOINTMENT_SLOT_MINUTES)

    event = calendar.create_event(
        summary=f"{reason} — {customer_name}",
        start=start,
        end=end,
        description=f"Booked via voice agent. Reason: {reason}",
        attendee_email=customer_email,
        extended_properties={"tenant_id": tenant_id, "reason": reason},
    )

    appointment_id = store.save_appointment(
        tenant_id,
        event["id"],
        {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "start_time": start.isoformat(),
            "reason": reason,
            "status": "booked",
        },
    )

    try:
        gmail.send_email(
            to=customer_email,
            subject=f"Appointment confirmed — {config.DEALERSHIP_NAME}",
            body_text=(
                f"Hi {customer_name},\n\n"
                f"Your appointment is confirmed for {start.strftime('%A, %B %d at %-I:%M %p')}.\n"
                f"Reason: {reason}\n\n"
                f"See you then,\n{config.DEALERSHIP_NAME}"
            ),
        )
        confirmation_sent = True
    except Exception:
        confirmation_sent = False

    return {
        "appointment_id": appointment_id,
        "calendar_event_id": event["id"],
        "start_time": start.isoformat(),
        "confirmation_email_sent": confirmation_sent,
    }


def reschedule_appointment(
    appointment_id: str, new_start_time: str, tenant_id: str = config.DEFAULT_TENANT_ID
) -> dict:
    """Move an existing appointment to a new start time."""
    record = store.get_appointment(appointment_id)
    if record is None:
        return {"error": f"No appointment found with id {appointment_id}"}

    new_start = datetime.fromisoformat(new_start_time)
    new_end = new_start + timedelta(minutes=config.APPOINTMENT_SLOT_MINUTES)

    calendar.update_event(record["calendar_event_id"], new_start, new_end)
    store.update_appointment(appointment_id, start_time=new_start.isoformat())

    try:
        gmail.send_email(
            to=record["customer_email"],
            subject=f"Appointment rescheduled — {config.DEALERSHIP_NAME}",
            body_text=(
                f"Hi {record['customer_name']},\n\n"
                f"Your appointment has been moved to "
                f"{new_start.strftime('%A, %B %d at %-I:%M %p')}.\n\n"
                f"{config.DEALERSHIP_NAME}"
            ),
        )
    except Exception:
        pass

    return {"appointment_id": appointment_id, "new_start_time": new_start.isoformat()}


def cancel_appointment(appointment_id: str, tenant_id: str = config.DEFAULT_TENANT_ID) -> dict:
    """Cancel an existing appointment."""
    record = store.get_appointment(appointment_id)
    if record is None:
        return {"error": f"No appointment found with id {appointment_id}"}

    calendar.delete_event(record["calendar_event_id"])
    store.update_appointment(appointment_id, status="cancelled")

    try:
        gmail.send_email(
            to=record["customer_email"],
            subject=f"Appointment cancelled — {config.DEALERSHIP_NAME}",
            body_text=(
                f"Hi {record['customer_name']},\n\n"
                f"Your appointment originally scheduled for "
                f"{datetime.fromisoformat(record['start_time']).strftime('%A, %B %d at %-I:%M %p')} "
                f"has been cancelled. Call us anytime to rebook.\n\n"
                f"{config.DEALERSHIP_NAME}"
            ),
        )
        confirmation_sent = True
    except Exception:
        confirmation_sent = False

    return {
        "appointment_id": appointment_id,
        "status": "cancelled",
        "confirmation_email_sent": confirmation_sent,
    }


def find_appointment(
    customer_email: str = "",
    customer_phone: str = "",
    tenant_id: str = config.DEFAULT_TENANT_ID,
) -> dict:
    """Look up existing appointment(s) by customer email or phone.

    Use this when a caller wants to reschedule or cancel a booking from an
    earlier call — they won't know the internal appointment_id, so ask for
    the email or phone number on the booking instead and call this first.
    """
    matches = store.find_appointments_by_contact(
        tenant_id, customer_email=customer_email, customer_phone=customer_phone
    )
    if not matches:
        return {"found": False, "appointments": []}
    return {"found": True, "appointments": matches}
