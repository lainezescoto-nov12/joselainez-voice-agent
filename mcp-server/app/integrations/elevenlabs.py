"""ElevenLabs outbound calling — used by trigger_outbound_reminder.

Places a real call directly through ElevenLabs' Twilio-backed outbound
endpoint. No workflow engine in between: the MCP server calls ElevenLabs
directly, same agent that handles inbound calls, just started outbound
with different context passed in via dynamic_variables.
"""
import httpx

from app import config

OUTBOUND_CALL_URL = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"


class ElevenLabsCallError(RuntimeError):
    pass


def place_outbound_call(
    to_number: str,
    customer_name: str,
    reminder_reason: str,
) -> dict:
    if not config.ELEVENLABS_API_KEY:
        raise ElevenLabsCallError("ELEVENLABS_API_KEY is not configured")
    if not config.ELEVENLABS_AGENT_ID or not config.ELEVENLABS_AGENT_PHONE_NUMBER_ID:
        raise ElevenLabsCallError(
            "ELEVENLABS_AGENT_ID / ELEVENLABS_AGENT_PHONE_NUMBER_ID are not configured"
        )

    payload = {
        "agent_id": config.ELEVENLABS_AGENT_ID,
        "agent_phone_number_id": config.ELEVENLABS_AGENT_PHONE_NUMBER_ID,
        "to_number": to_number,
        "conversation_initiation_client_data": {
            "conversation_config_override": {
                "agent": {
                    "first_message": (
                        f"Hi {{{{customer_name}}}}, this is {config.DEALERSHIP_NAME} "
                        "calling with a quick reminder — {{reminder_reason}}. "
                        "Do you have a moment?"
                    )
                }
            },
            "dynamic_variables": {
                "customer_name": customer_name or "there",
                "reminder_reason": reminder_reason,
                # So the agent can look up the appointment itself (via
                # find_appointment) without asking the person it just
                # called to identify themselves -- it's already calling
                # their number.
                "customer_phone": to_number,
            },
        },
    }

    response = httpx.post(
        OUTBOUND_CALL_URL,
        json=payload,
        headers={"xi-api-key": config.ELEVENLABS_API_KEY},
        timeout=15.0,
    )
    response.raise_for_status()
    return response.json()
