"""check_part_availability -- looks up whether a part is in stock for a
given vehicle, calling the n8n parts-availability workflow directly and
synchronously. Unlike the old outbound-reminder n8n design (fire-and-
forget), a caller asking about parts needs a live answer during the call,
so this waits for n8n's response instead of just queueing a request.
"""
import httpx

from app import config


class PartsLookupError(RuntimeError):
    pass


def check_part_availability(
    part_name: str,
    vehicle_make: str,
    vehicle_model: str,
    vehicle_year: str = "",
    tenant_id: str = config.DEFAULT_TENANT_ID,
) -> dict:
    """Check whether a part is in stock for a given vehicle."""
    if not config.N8N_PARTS_WEBHOOK_URL:
        raise PartsLookupError("N8N_PARTS_WEBHOOK_URL is not configured")

    response = httpx.post(
        config.N8N_PARTS_WEBHOOK_URL,
        json={
            "part_name": part_name,
            "vehicle_make": vehicle_make,
            "vehicle_model": vehicle_model,
            "vehicle_year": vehicle_year,
            "tenant_id": tenant_id,
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
