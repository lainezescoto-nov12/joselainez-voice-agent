"""Run this ONCE, locally, to grant Calendar + Gmail consent and store the
resulting refresh token in GCP Secret Manager.

Why this exists: the OAuth client (`credentials.json`, downloaded from GCP
Console) is a Desktop-app client, which requires an interactive browser
consent screen. Cloud Run is unattended — it can never show that screen. So
this script is the one place the interactive flow happens; everything the
deployed server does afterward runs off the long-lived refresh token this
script produces, read from Secret Manager (see app/integrations/google_auth.py).

Usage:
    cd mcp-server
    python -m scripts.one_time_oauth_setup \\
        --credentials /path/to/credentials.json \\
        --project vintti-voice-agent

This opens a browser for consent, then creates (or adds a new version to)
the `dealership-google-refresh-token` secret in Secret Manager. The refresh
token is never printed to stdout and never written to disk.
"""
import argparse

from google_auth_oauthlib.flow import InstalledAppFlow
from google.cloud import secretmanager
from google.api_core.exceptions import AlreadyExists

from app import config

SCOPES = config.GOOGLE_OAUTH_SCOPES


def run_consent_flow(credentials_path: str) -> str:
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    # access_type=offline + prompt=consent is required to force Google to
    # actually issue a refresh token (it's silently omitted on repeat
    # consents otherwise).
    creds = flow.run_local_server(
        port=0, access_type="offline", prompt="consent"
    )
    if not creds.refresh_token:
        raise RuntimeError(
            "No refresh token returned. Revoke prior access at "
            "https://myaccount.google.com/permissions and re-run."
        )
    return creds.refresh_token


def store_in_secret_manager(project_id: str, secret_id: str, refresh_token: str) -> None:
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project_id}"
    secret_name = f"{parent}/secrets/{secret_id}"

    try:
        client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        print(f"Created secret {secret_id}")
    except AlreadyExists:
        print(f"Secret {secret_id} already exists, adding a new version")

    client.add_secret_version(
        request={
            "parent": secret_name,
            "payload": {"data": refresh_token.encode("utf-8")},
        }
    )
    print(f"Stored new refresh token in {secret_name}/versions/latest")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--credentials",
        required=True,
        help="Path to the downloaded Desktop OAuth client JSON",
    )
    parser.add_argument(
        "--project",
        default=config.GCP_PROJECT_ID,
        help="GCP project to store the secret in",
    )
    parser.add_argument(
        "--secret-id",
        default=config.GOOGLE_REFRESH_TOKEN_SECRET,
        help="Secret Manager secret name",
    )
    args = parser.parse_args()

    refresh_token = run_consent_flow(args.credentials)
    store_in_secret_manager(args.project, args.secret_id, refresh_token)

    print(
        "\nDone. The refresh token is now in Secret Manager, not on disk.\n"
        "Make sure the Cloud Run service account has "
        "'Secret Manager Secret Accessor' on this secret, and that "
        "GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET are set as "
        "env vars on the service (same values as this credentials.json)."
    )


if __name__ == "__main__":
    main()
