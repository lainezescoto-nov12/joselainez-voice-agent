"""Places the real outbound demo call via ElevenLabs.

Deliberately a near-duplicate of mcp-server/app/integrations/elevenlabs.py --
these are two independently deployed services with different exposure
profiles (internal tool server vs. public demo API), so a small amount of
duplication here is the honest tradeoff over coupling them together.
"""
import httpx

from app import config

OUTBOUND_CALL_URL = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"


class ElevenLabsCallError(RuntimeError):
    pass


def place_demo_call(to_number: str) -> dict:
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
                        f"Hi, this is {config.DEALERSHIP_NAME} — thanks for trying "
                        "the live voice agent demo from the portfolio. Feel free to "
                        "ask about booking a test drive, checking a vehicle's "
                        "status, or anything else this agent can help with."
                    )
                }
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
