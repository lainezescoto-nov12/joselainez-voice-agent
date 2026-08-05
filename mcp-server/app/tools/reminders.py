"""trigger_outbound_reminder — places a real outbound call directly via ElevenLabs.

Manual-trigger only: something in the current conversation (a staff member
using the agent, or an explicit instruction) asks for a reminder call to go
out to one specific customer right now. This is not a scheduled sweep —
there is no cron here. A systematic "everyone due for service" sweep would
need a separate trigger (e.g. Cloud Scheduler calling a dedicated endpoint)
and is explicitly out of scope for this tool.
"""
from app import config
from app.integrations import elevenlabs


def trigger_outbound_reminder(
    customer_phone: str,
    customer_name: str,
    reminder_reason: str,
    tenant_id: str = config.DEFAULT_TENANT_ID,
) -> dict:
    """Place a real outbound reminder call to a customer right now."""
    result = elevenlabs.place_outbound_call(
        to_number=customer_phone,
        customer_name=customer_name,
        reminder_reason=reminder_reason,
    )
    return {
        "tenant_id": tenant_id,
        "call_placed": bool(result.get("success")),
        "conversation_id": result.get("conversation_id"),
        "call_sid": result.get("callSid"),
    }
