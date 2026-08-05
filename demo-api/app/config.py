"""Config for the public demo-call API. Deliberately separate from
mcp-server/app/config.py -- this service has a different exposure profile
(public, unauthenticated) and is deployed independently, so it keeps its
own env vars even where they overlap (ELEVENLABS_*, GCP project).
"""
import os

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vintti-voice-agent")

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_VERIFY_SERVICE_SID = os.environ.get("TWILIO_VERIFY_SERVICE_SID", "")

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_AGENT_ID = os.environ.get("ELEVENLABS_AGENT_ID", "")
ELEVENLABS_AGENT_PHONE_NUMBER_ID = os.environ.get("ELEVENLABS_AGENT_PHONE_NUMBER_ID", "")

DEALERSHIP_NAME = os.environ.get("DEALERSHIP_NAME", "Ridgeline Auto Group")

# Comma-separated list of origins allowed to call this API from a browser.
# Set to the actual portfolio domain(s) in production -- "*" is fine only
# while testing locally/from Vercel preview URLs.
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

# How often the same phone number can trigger a real call, regardless of
# how many times they pass OTP verification. This is the actual abuse
# brake -- OTP proves consent once, this caps repeat use.
RATE_LIMIT_HOURS = int(os.environ.get("RATE_LIMIT_HOURS", "24"))
