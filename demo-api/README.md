# Demo Call API

Public, unauthenticated (by design) API that powers the "Try the AI voice
Agent-Outbound Live Demo call" widget on the portfolio site. Lets a visitor
type their phone number and receive a real outbound call from the
dealership voice agent.

Deployed as its own Cloud Run service, separate from `mcp-server` — this
one is meant to be hit directly from a browser (CORS-enabled), the MCP
server is not (it only ever talks to ElevenLabs' MCP client).

## Why OTP, not just "type a number and get called"

An open endpoint that calls any number a visitor types is a real abuse and
regulatory risk (unsolicited automated calls are legally regulated —
robocall/consent laws — and almost certainly a Twilio Acceptable Use
Policy violation). The flow here is deliberately two steps:

1. `POST /verify/send` — sends a one-time code via **Twilio Verify** to
   the number provided. Proves the requester actually controls that
   number before anything calls it.
2. `POST /verify/check` — checks the code. Only on success does it check
   the Firestore-backed rate limit (`RATE_LIMIT_HOURS`, default 24h per
   number) and then place the real call via ElevenLabs' outbound API.

The rate limit matters even after a successful OTP check — it's what
stops the same (now-verified) number from being called repeatedly.

## Setup

### 1. Create a Twilio Verify Service (one-time, in Twilio Console)

Twilio Console → **Verify** → **Services** → Create new service (any
name, e.g. "Ridgeline Demo Verification"). Copy the **Service SID**
(starts with `VA...`) — that's `TWILIO_VERIFY_SERVICE_SID`.

### 2. Env vars

```
GCP_PROJECT_ID=vintti-voice-agent
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_VERIFY_SERVICE_SID=VA...
ELEVENLABS_API_KEY=...
ELEVENLABS_AGENT_ID=...
ELEVENLABS_AGENT_PHONE_NUMBER_ID=...
DEALERSHIP_NAME=Ridgeline Auto Group
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app
RATE_LIMIT_HOURS=24
```

`TWILIO_AUTH_TOKEN` and `ELEVENLABS_API_KEY` as plain env vars here is the
same speed-over-hardening tradeoff made for the MCP server's OAuth client
secret — fine for a demo, would move to Secret Manager for anything
beyond that.

### 3. Deploy

```bash
cd demo-api
gcloud run deploy dealership-demo-api \
  --source . \
  --project vintti-voice-agent \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=vintti-voice-agent,TWILIO_ACCOUNT_SID=...,TWILIO_AUTH_TOKEN=...,TWILIO_VERIFY_SERVICE_SID=VA...,ELEVENLABS_API_KEY=...,ELEVENLABS_AGENT_ID=...,ELEVENLABS_AGENT_PHONE_NUMBER_ID=...,DEALERSHIP_NAME=Ridgeline Auto Group,ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app" \
  --quiet
```

Grant this service's compute service account the same `roles/datastore.user`
already granted for the MCP server's Firestore access — same project, same
role, one binding covers both services.

### 4. Wire the frontend

Set `NEXT_PUBLIC_DEMO_API_URL` in the Next.js app's environment (Vercel
project settings, or `.env.local` for local dev) to this service's Cloud
Run URL. The `OutboundDemoCall` widget on the main page reads this at
build/runtime — without it, the widget shows a clear "not configured"
message instead of silently failing.

## Known tradeoffs

- Firestore rate limit is per-phone-number, not per-IP — someone could
  still spam OTP *sends* to different numbers from one IP, running up
  Twilio Verify costs (cheap, but not free) without ever completing a
  call. Not addressed here; a per-IP limit on `/verify/send` would be the
  next hardening step if this saw real traffic.
- No CAPTCHA — acceptable for a portfolio demo's expected traffic level,
  would reconsider for anything with real public exposure.
