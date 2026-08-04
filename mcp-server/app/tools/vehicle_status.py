"""check_vehicle_status — service status + recall lookup by VIN."""
from app import config
from app.data.mock_inventory import VEHICLES_BY_VIN


def check_vehicle_status(vin: str, tenant_id: str = config.DEFAULT_TENANT_ID) -> dict:
    """Look up service status and any open recall for a VIN."""
    vehicle = VEHICLES_BY_VIN.get(vin.upper())
    if vehicle is None:
        return {"error": f"No record found for VIN {vin}"}
    return vehicle
