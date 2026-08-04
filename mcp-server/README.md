# Dealership Voice Agent — MCP Server

FastMCP (Python) tool server for the ElevenLabs dealership voice agent.
Deployed to GCP Cloud Run in the `vintti-voice-agent` project. Once deployed,
its URL goes into the ElevenLabs agent's Tools section as an MCP server URL.

## Tools

| Tool | Purpose |
|---|---|
| `check_availability` | Open appointment slots on a given day (Calendar freebusy) |
| `book_appointment` | Books a Calendar event + sends a Gmail confirmation |
| `reschedule_appointment` | Moves an existing appointment |
| `cancel_appointment` | Cancels an existing appointment + sends a Gmail cancellation notice |
| `find_appointment` | Looks up an existing appointment by customer email/phone — needed when a caller references a booking from an earlier call and doesn't have the internal appointment_id |
| `intake_trade_in` | Captures trade-in details, returns a ballpark estimate + a `suggested_next_action` hint so the agent chains into booking a test drive |
| `check_vehicle_status` | Service status + open recall lookup by VIN |
| `dealership_faq_lookup` | Answers general questions from a small static KB |
| `trigger_notification` | Hands off confirmation/reschedule/cancellation emails to n8n |
| `trigger_outbound_reminder` | Hands off the outbound proactive service-reminder call sequence to n8n |

## Why the Google auth is two steps, not one

The OAuth client (`credentials.json`, downloaded from GCP Console) is a
**Desktop-app** client. That type only supports interactive browser consent —
which Cloud Run, an unattended service, can never show. So the flow is split:

1. **One-time, local**: `scripts/one_time_oauth_setup.py` runs the interactive
   consent flow on your machine and stores the resulting **refresh token** in
   GCP Secret Manager. The token is never written to disk or printed.
2. **Every request, on Cloud Run**: `app/integrations/google_auth.py` reads
   that refresh token from Secret Manager and mints a short-lived access
   token from it. No interactive step, no credentials baked into the image
   or committed to the repo.

```
local consent (once) --> refresh token --> Secret Manager
                                                 |
                          Cloud Run reads it per request, refreshes
                          the access token transparently
```

### Running the one-time setup

```bash
cd mcp-server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m scripts.one_time_oauth_setup \
  --credentials /path/to/your/downloaded/credentials.json \
  --project vintti-voice-agent
```

This opens a browser, asks for Calendar + Gmail consent, and stores the
refresh token as the `dealership-google-refresh-token` secret. Grant the
Cloud Run service account **Secret Manager Secret Accessor** on that secret:

```bash
gcloud secrets add-iam-policy-binding dealership-google-refresh-token \
  --project vintti-voice-agent \
  --member "serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role "roles/secretmanager.secretAccessor"
```

## Appointment persistence (Firestore)

`book_appointment`, `reschedule_appointment`, `cancel_appointment`, and
`find_appointment` all read/write through `app/data/store.py`, which is
backed by **Firestore (Native mode)** — not an in-memory dict. This matters
specifically for `find_appointment`: a caller referencing a booking made in
a *previous* call has no way to hand back an internal ID, so lookup has to
survive past the process that created the record, across Cloud Run cold
starts and instances.

One-time setup:

```bash
gcloud services enable firestore.googleapis.com --project vintti-voice-agent

# If this project has never had a Firestore database, create one (Native
# mode; pick a region — us-central1 to match Cloud Run is fine):
gcloud firestore databases create --project vintti-voice-agent --location us-central1

PROJECT_NUMBER=$(gcloud projects describe vintti-voice-agent --format="value(projectNumber)")
gcloud projects add-iam-policy-binding vintti-voice-agent \
  --member "serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role "roles/datastore.user"
```

`find_appointment` filters on `tenant_id` plus `customer_email` or
`customer_phone` — both equality filters, so this works without a
composite index. If a future query adds an inequality filter or ordering,
Firestore will return an error containing a direct link to create the
needed index; follow that link rather than guessing at index config.

## Deploying

No local Docker needed — `--source` hands the build off to Cloud Build via
buildpacks (this repo's `requirements.txt` + `Procfile` are what buildpacks
auto-detect).

```bash
cd mcp-server
gcloud config set project vintti-voice-agent

gcloud run deploy dealership-mcp-server \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "GCP_PROJECT_ID=vintti-voice-agent,GOOGLE_OAUTH_CLIENT_ID=...,GOOGLE_OAUTH_CLIENT_SECRET=...,SERVICE_CALENDAR_ID=...,DEALERSHIP_FROM_EMAIL=...,N8N_BASE_URL=..."
```

(`GOOGLE_OAUTH_CLIENT_ID`/`SECRET` are the same values from the Desktop
client JSON — they identify the app, not a user, so they're fine as plain
env vars; only the refresh token needs Secret Manager.)

`--allow-unauthenticated` is scoped to this being a portfolio demo behind an
otherwise-unguarded MCP endpoint; for anything beyond a demo, front it with
IAM auth or a shared-secret header check.

After deploy, `gcloud run deploy` prints the service URL
(`https://dealership-mcp-server-xxxxx-uc.a.run.app`). Paste that into the
ElevenLabs agent's **Tools → MCP Server URL** field to connect the agent to
real tool-calling.

## Local dev

```bash
cp .env.example .env   # fill in values
source .venv/bin/activate
python -m app.server    # serves on http://localhost:8080
```

## Deploy troubleshooting

### `PermissionDenied` on Cloud Build source/Artifact Registry buckets

Newer GCP projects don't auto-grant the legacy default Editor/Viewer roles
to the compute service account (`PROJECT_NUMBER-compute@developer.gserviceaccount.com`)
the way older projects did. If `gcloud run deploy --source .` fails with a
permissions error reading the Cloud Build source bucket
(`run-sources-*` or `PROJECT_ID_cloudbuild`) or pushing to the
`cloud-run-source-deploy` Artifact Registry repo, this is almost certainly
why — check IAM before assuming anything else is misconfigured.

Fix (project-level, covers every future source-based deploy, not just one bucket):

```bash
PROJECT_NUMBER=$(gcloud projects describe vintti-voice-agent --format="value(projectNumber)")
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding vintti-voice-agent \
  --member "serviceAccount:${SA}" --role "roles/storage.objectViewer"
gcloud projects add-iam-policy-binding vintti-voice-agent \
  --member "serviceAccount:${SA}" --role "roles/logging.logWriter"
gcloud projects add-iam-policy-binding vintti-voice-agent \
  --member "serviceAccount:${SA}" --role "roles/artifactregistry.writer"
```

If Cloud Build logs come back empty/inaccessible, the Cloud Build service
account (`PROJECT_NUMBER@cloudbuild.gserviceaccount.com`) may also need
`roles/logging.logWriter`.

### `Error 403: org_internal` during the one-time OAuth consent

The OAuth consent screen (**Google Auth Platform → Audience** in GCP
Console) defaulted to **User type: Internal**, which only allows accounts
inside a Workspace org to consent — a personal Gmail account gets blocked
before it even sees the permission screen. Fix: set **User type: External**,
leave **Publishing status: Testing**, and add the consenting Gmail address
under **Test users**. Testing-status apps show an "unverified app" warning
in the consent screen — click through Advanced → "Go to (app name)
(unsafe)"; that's expected for an unpublished demo app, not a real problem.

### Naive-datetime timezone bug (fixed, but a general lesson)

`check_availability` originally called `.astimezone(tz)` on a naive
`datetime` parsed from a date-only string. A naive `datetime` gets silently
treated as being in the *system's local timezone* (UTC on Cloud Run) before
converting — so a request for a date in `America/New_York` (UTC behind)
came back shifted a day. Local testing didn't catch it; a smoke test
against the real deployed service did. Fixed in
`app/integrations/calendar.py` by calling `.replace(tzinfo=tz)` on naive
input instead of `.astimezone()`.

## Known v2 tradeoffs (by design, not oversight)

- **Firestore store** (`app/data/store.py`) for trade-in/appointment
  records — real persistence, but no schema migrations, no transactions
  beyond single-document updates, and `find_appointment` is a simple
  equality-filter lookup, not a real customer-matching system (a caller
  who gives a slightly different email/phone than what was booked won't
  match). Fine for a single-tenant demo; v3's multi-tenant version needs a
  real customer identity model on top of this, not just more Firestore.
- **Static FAQ KB + keyword scoring**, not embeddings — the KB is a handful
  of entries; not worth a vector store yet.
- **`tenant_id` threaded through every tool and record** even though v2 only
  ever runs with one tenant — so v3 (LA Solutions multi-tenant platform)
  doesn't need a data migration, just a real tenant resolver.
