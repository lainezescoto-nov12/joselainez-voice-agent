"""n8n webhook dispatch for the two trigger_* tools.

These two tools deliberately don't call Gmail/Twilio/etc. directly. n8n owns
the notification/reminder *workflows* (retries, templating, the outbound
call sequence orchestration) so that logic can change without a server
redeploy — the MCP server's job is just to hand off the event with enough
context to act on.
"""
import httpx

from app import config


class N8nDispatchError(RuntimeError):
    pass


def _post(path: str, payload: dict) -> dict:
    if not config.N8N_BASE_URL:
        raise N8nDispatchError("N8N_BASE_URL is not configured")

    url = f"{config.N8N_BASE_URL.rstrip('/')}{path}"
    headers = {}
    if config.N8N_WEBHOOK_SECRET:
        headers["X-Webhook-Secret"] = config.N8N_WEBHOOK_SECRET

    response = httpx.post(url, json=payload, headers=headers, timeout=10.0)
    response.raise_for_status()
    return {"status": "dispatched", "n8n_status_code": response.status_code}


def trigger_notification(payload: dict) -> dict:
    return _post(config.N8N_NOTIFICATION_WEBHOOK_PATH, payload)


def trigger_outbound_reminder(payload: dict) -> dict:
    return _post(config.N8N_OUTBOUND_REMINDER_WEBHOOK_PATH, payload)
