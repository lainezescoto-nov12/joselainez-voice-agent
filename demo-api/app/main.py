"""Public demo-call API.

Two endpoints, both meant to be called from a browser on the portfolio
site:
  POST /verify/send   -- send an OTP to a phone number via Twilio Verify
  POST /verify/check  -- check the OTP; if correct AND the number hasn't
                          used the demo recently, place a real outbound
                          call via ElevenLabs

The OTP step is the actual consent mechanism (proves the requester
controls the number before anything calls it); the rate limit caps repeat
use by the same number even after a successful verification. Neither
alone is enough -- an open "call any number" endpoint is a real abuse and
regulatory (robocall/consent) risk, this is the guardrail for that.
"""
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import config, elevenlabs, rate_limit, twilio_verify

app = FastAPI(title="Dealership Voice Agent - Demo Call API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")


def _validate_phone(phone_number: str) -> str:
    phone_number = phone_number.strip()
    if not E164_RE.match(phone_number):
        raise HTTPException(
            status_code=400,
            detail="Phone number must be in E.164 format, e.g. +50432964465",
        )
    return phone_number


class SendCodeRequest(BaseModel):
    phone_number: str


class CheckCodeRequest(BaseModel):
    phone_number: str
    code: str


@app.post("/verify/send")
def verify_send(body: SendCodeRequest):
    phone_number = _validate_phone(body.phone_number)
    try:
        twilio_verify.send_code(phone_number)
    except (twilio_verify.TwilioVerifyError, Exception) as exc:
        raise HTTPException(status_code=502, detail=f"Could not send verification code: {exc}")
    return {"sent": True}


@app.post("/verify/check")
def verify_check(body: CheckCodeRequest):
    phone_number = _validate_phone(body.phone_number)

    try:
        approved = twilio_verify.check_code(phone_number, body.code)
    except (twilio_verify.TwilioVerifyError, Exception) as exc:
        raise HTTPException(status_code=502, detail=f"Could not check verification code: {exc}")

    if not approved:
        raise HTTPException(status_code=400, detail="Incorrect or expired code.")

    allowed, reason = rate_limit.check(phone_number)
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)

    try:
        result = elevenlabs.place_demo_call(phone_number)
    except (elevenlabs.ElevenLabsCallError, Exception) as exc:
        raise HTTPException(status_code=502, detail=f"Could not place the call: {exc}")

    call_placed = bool(result.get("success"))
    if call_placed:
        rate_limit.record(phone_number)

    return {"call_placed": call_placed, "conversation_id": result.get("conversation_id")}


@app.get("/convai/signed-url")
def convai_signed_url():
    """For the browser widget: mint a signed URL server-side so the
    ElevenLabs API key never has to reach the browser. Only needed if the
    agent is private -- a public agent can start a session with just its
    agent_id, no call to this endpoint at all.
    """
    try:
        signed_url = elevenlabs.get_signed_url()
    except (elevenlabs.ElevenLabsCallError, Exception) as exc:
        raise HTTPException(status_code=502, detail=f"Could not get signed URL: {exc}")
    return {"signedUrl": signed_url}


@app.get("/health")
def health():
    return {"status": "ok"}
