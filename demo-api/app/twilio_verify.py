"""Twilio Verify -- OTP send/check. Using the REST API directly via httpx
(same pattern as everywhere else in this project) rather than pulling in
the full Twilio SDK for two endpoints.
"""
import httpx

from app import config

BASE_URL = f"https://verify.twilio.com/v2/Services/{{service_sid}}"


class TwilioVerifyError(RuntimeError):
    pass


def _auth() -> tuple[str, str]:
    if not config.TWILIO_ACCOUNT_SID or not config.TWILIO_AUTH_TOKEN:
        raise TwilioVerifyError("TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN not configured")
    return (config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)


def send_code(phone_number: str) -> dict:
    if not config.TWILIO_VERIFY_SERVICE_SID:
        raise TwilioVerifyError("TWILIO_VERIFY_SERVICE_SID not configured")

    url = BASE_URL.format(service_sid=config.TWILIO_VERIFY_SERVICE_SID) + "/Verifications"
    response = httpx.post(
        url,
        auth=_auth(),
        data={"To": phone_number, "Channel": "sms"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()


def check_code(phone_number: str, code: str) -> bool:
    if not config.TWILIO_VERIFY_SERVICE_SID:
        raise TwilioVerifyError("TWILIO_VERIFY_SERVICE_SID not configured")

    url = BASE_URL.format(service_sid=config.TWILIO_VERIFY_SERVICE_SID) + "/VerificationCheck"
    response = httpx.post(
        url,
        auth=_auth(),
        data={"To": phone_number, "Code": code},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json().get("status") == "approved"
