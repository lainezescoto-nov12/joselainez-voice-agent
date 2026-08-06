"""Central config, all sourced from environment variables (Cloud Run env / Secret Manager)."""
import os

# GCP
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "vintti-voice-agent")

# Secret Manager secret name holding the OAuth refresh token minted by
# scripts/one_time_oauth_setup.py. Version is always "latest".
GOOGLE_REFRESH_TOKEN_SECRET = os.environ.get(
    "GOOGLE_REFRESH_TOKEN_SECRET", "dealership-google-refresh-token"
)

# OAuth client id/secret are not secret-sensitive the way the refresh token is
# (they identify the app, not a user), but still kept out of source control.
GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

GOOGLE_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
]

# Calendar used for service appointments / test drives.
SERVICE_CALENDAR_ID = os.environ.get("SERVICE_CALENDAR_ID", "primary")

# From address for confirmation/reschedule emails sent via Gmail API.
DEALERSHIP_FROM_EMAIL = os.environ.get("DEALERSHIP_FROM_EMAIL", "")
DEALERSHIP_NAME = os.environ.get("DEALERSHIP_NAME", "Ridgeline Auto Group")

# ElevenLabs outbound calling — used by trigger_outbound_reminder to place a
# real call directly, no workflow engine in between.
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_AGENT_ID = os.environ.get("ELEVENLABS_AGENT_ID", "")
ELEVENLABS_AGENT_PHONE_NUMBER_ID = os.environ.get("ELEVENLABS_AGENT_PHONE_NUMBER_ID", "")

# n8n parts-availability workflow. Synchronous, unlike the old outbound-
# reminder n8n design -- a caller asking about parts needs a live answer
# during the call, not a queued fire-and-forget.
N8N_PARTS_WEBHOOK_URL = os.environ.get(
    "N8N_PARTS_WEBHOOK_URL", "https://lainezescoto.app.n8n.cloud/webhook/parts-availability"
)

# v2 is single-tenant, but every record carries tenant_id so v3 (LA Solutions
# multi-tenant platform) can shard on it without a data migration.
DEFAULT_TENANT_ID = os.environ.get("DEFAULT_TENANT_ID", "vintti-demo")

APPOINTMENT_SLOT_MINUTES = int(os.environ.get("APPOINTMENT_SLOT_MINUTES", "30"))
BUSINESS_HOURS_START = int(os.environ.get("BUSINESS_HOURS_START", "9"))
BUSINESS_HOURS_END = int(os.environ.get("BUSINESS_HOURS_END", "18"))
BUSINESS_TIMEZONE = os.environ.get("BUSINESS_TIMEZONE", "America/New_York")
