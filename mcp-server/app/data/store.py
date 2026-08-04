"""In-process record store for trade-in intake and appointment metadata.

Deliberately not a real database for this build: v2 is a single-tenant
portfolio piece, and Cloud Run's default single-instance-per-request-burst
behavior makes an in-memory dict "work" for a live demo. It will NOT survive
a cold start or scale past one instance — that's the known, called-out
tradeoff. v3 (LA Solutions multi-tenant platform) is where this becomes
Firestore/Cloud SQL, keyed on the tenant_id every record already carries.
"""
import itertools
import threading
from typing import Any

_lock = threading.Lock()
_trade_ins: dict[str, dict[str, Any]] = {}
_appointments: dict[str, dict[str, Any]] = {}
_id_counter = itertools.count(1)


def _next_id(prefix: str) -> str:
    return f"{prefix}-{next(_id_counter):05d}"


def save_trade_in(tenant_id: str, record: dict[str, Any]) -> str:
    trade_in_id = _next_id("trade")
    with _lock:
        _trade_ins[trade_in_id] = {"tenant_id": tenant_id, **record}
    return trade_in_id


def get_trade_in(trade_in_id: str) -> dict[str, Any] | None:
    return _trade_ins.get(trade_in_id)


def save_appointment(tenant_id: str, event_id: str, record: dict[str, Any]) -> str:
    appointment_id = _next_id("appt")
    with _lock:
        _appointments[appointment_id] = {
            "tenant_id": tenant_id,
            "calendar_event_id": event_id,
            **record,
        }
    return appointment_id


def get_appointment(appointment_id: str) -> dict[str, Any] | None:
    return _appointments.get(appointment_id)


def update_appointment(appointment_id: str, **fields: Any) -> None:
    with _lock:
        if appointment_id in _appointments:
            _appointments[appointment_id].update(fields)
