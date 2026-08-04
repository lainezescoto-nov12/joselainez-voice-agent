"""intake_trade_in — deliberately returns a `suggested_next_action` hint so the
agent's LLM has an explicit signal to chain into check_availability /
book_appointment for a test drive, rather than relying on it to infer that
from prose. This is the tool-chaining differentiator use case.
"""
from app import config
from app.data import store

# Rough condition multipliers against a flat base value per make/model tier.
# Stand-in for a real valuation API (e.g. KBB/Black Book) integration.
_BASE_VALUES = {
    "economy": 8000,
    "midsize": 14000,
    "luxury": 24000,
    "truck_suv": 18000,
}
_CONDITION_MULTIPLIER = {"excellent": 1.15, "good": 1.0, "fair": 0.8, "poor": 0.55}


def intake_trade_in(
    customer_name: str,
    vehicle_year: int,
    vehicle_make: str,
    vehicle_model: str,
    mileage: int,
    condition: str,
    vehicle_tier: str = "midsize",
    tenant_id: str = config.DEFAULT_TENANT_ID,
) -> dict:
    """Capture trade-in details and return a ballpark estimate."""
    base = _BASE_VALUES.get(vehicle_tier, _BASE_VALUES["midsize"])
    multiplier = _CONDITION_MULTIPLIER.get(condition.lower(), 0.85)
    mileage_penalty = max(0, (mileage - 60000)) * 0.03
    estimate = round(max(base * multiplier - mileage_penalty, 500))

    trade_in_id = store.save_trade_in(
        tenant_id,
        {
            "customer_name": customer_name,
            "vehicle_year": vehicle_year,
            "vehicle_make": vehicle_make,
            "vehicle_model": vehicle_model,
            "mileage": mileage,
            "condition": condition,
            "estimate_usd": estimate,
        },
    )

    return {
        "trade_in_id": trade_in_id,
        "estimated_value_usd": estimate,
        "estimate_note": "Ballpark only — final offer requires an in-person inspection.",
        "suggested_next_action": (
            "Offer to book a test drive and in-person trade-in appraisal via "
            "check_availability + book_appointment; pass reason='Trade-in appraisal + test drive'."
        ),
    }
