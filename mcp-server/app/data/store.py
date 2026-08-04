"""Firestore-backed record store for trade-in intake and appointment metadata.

Firestore Native mode, project-wide database — appointments and trade-ins
are top-level collections. Records persist across calls and Cloud Run cold
starts, which an earlier in-memory version of this file deliberately did
not (see git history) — persistence is required for find_appointments_by_contact
to work: a caller referencing a booking made in a previous call has no way
to hand back an internal appointment_id, so lookups have to survive past
the process that created the record.
"""
from typing import Any

from google.cloud import firestore

from app import config

_client: firestore.Client | None = None


def _db() -> firestore.Client:
    global _client
    if _client is None:
        _client = firestore.Client(project=config.GCP_PROJECT_ID)
    return _client


def save_trade_in(tenant_id: str, record: dict[str, Any]) -> str:
    doc_ref = _db().collection("trade_ins").document()
    doc_ref.set({"tenant_id": tenant_id, **record})
    return doc_ref.id


def get_trade_in(trade_in_id: str) -> dict[str, Any] | None:
    doc = _db().collection("trade_ins").document(trade_in_id).get()
    return doc.to_dict() if doc.exists else None


def save_appointment(tenant_id: str, event_id: str, record: dict[str, Any]) -> str:
    doc_ref = _db().collection("appointments").document()
    doc_ref.set({"tenant_id": tenant_id, "calendar_event_id": event_id, **record})
    return doc_ref.id


def get_appointment(appointment_id: str) -> dict[str, Any] | None:
    doc = _db().collection("appointments").document(appointment_id).get()
    return doc.to_dict() if doc.exists else None


def update_appointment(appointment_id: str, **fields: Any) -> None:
    _db().collection("appointments").document(appointment_id).update(fields)


def find_appointments_by_contact(
    tenant_id: str,
    customer_email: str = "",
    customer_phone: str = "",
    active_only: bool = True,
) -> list[dict[str, Any]]:
    """Look up appointments by customer email or phone.

    Needed so a caller can reference a booking made in an earlier call —
    they have no way to know the internal appointment_id, so lookup has to
    go through something they'd actually say out loud.
    """
    if not customer_email and not customer_phone:
        return []

    query = _db().collection("appointments").where("tenant_id", "==", tenant_id)
    if customer_email:
        query = query.where("customer_email", "==", customer_email)
    elif customer_phone:
        query = query.where("customer_phone", "==", customer_phone)

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        if active_only and data.get("status") == "cancelled":
            continue
        results.append({"appointment_id": doc.id, **data})
    return results
