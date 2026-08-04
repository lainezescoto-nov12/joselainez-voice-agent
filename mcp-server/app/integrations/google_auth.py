"""Server-side Google credentials, minted from a refresh token in Secret Manager.

The OAuth client is a Desktop-app type, which only supports interactive
browser consent — that flow cannot run unattended inside Cloud Run. So the
consent step happens exactly once, locally (see scripts/one_time_oauth_setup.py),
and everything after that is refresh-token-only:

    local consent (one time)  -->  refresh token  -->  GCP Secret Manager
                                                              |
                                    Cloud Run reads it at runtime, per request
                                    (google-auth refreshes the access token
                                    transparently; nothing is ever baked into
                                    the image or committed to the repo).
"""
import functools

from google.auth.transport.requests import Request
from google.cloud import secretmanager
from google.oauth2.credentials import Credentials

from app import config


@functools.lru_cache(maxsize=1)
def _secret_manager_client() -> secretmanager.SecretManagerServiceClient:
    return secretmanager.SecretManagerServiceClient()


def _fetch_refresh_token() -> str:
    client = _secret_manager_client()
    name = (
        f"projects/{config.GCP_PROJECT_ID}/secrets/"
        f"{config.GOOGLE_REFRESH_TOKEN_SECRET}/versions/latest"
    )
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8").strip()


def get_credentials() -> Credentials:
    """Build live Google API credentials for this request.

    Each call re-fetches the refresh token from Secret Manager (cheap, and
    it means a rotated secret takes effect without redeploying the service)
    and lets google-auth mint a fresh access token from it.
    """
    if not config.GOOGLE_OAUTH_CLIENT_ID or not config.GOOGLE_OAUTH_CLIENT_SECRET:
        raise RuntimeError(
            "GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET are not set. "
            "These are the same values from the Desktop OAuth client JSON, "
            "set as Cloud Run env vars."
        )

    creds = Credentials(
        token=None,
        refresh_token=_fetch_refresh_token(),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=config.GOOGLE_OAUTH_CLIENT_SECRET,
        scopes=config.GOOGLE_OAUTH_SCOPES,
    )
    creds.refresh(Request())
    return creds
