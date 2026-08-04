"""trigger_notification, trigger_outbound_reminder — hand-offs to n8n.

Why n8n instead of calling Gmail/Twilio directly for these two: the
appointment tools need a synchronous result (booked / not booked) the agent
speaks back immediately, so they call Calendar/Gmail inline. These two are
fire-and-forget side effects (a confirmation email template, an outbound
call sequence) whose orchestration — retries, templating, scheduling — is
better owned by a workflow tool than baked into agent-tool-call latency.
"""
from app import config
from app.integrations import n8n


def trigger_notification(
    customer_email: str,
    notification_type: str,
    context: str,
    tenant_id: str = config.DEFAULT_TENANT_ID,
) -> dict:
    """Hand off a confirmation/reschedule/cancellation notification to n8n.

    notification_type: one of "confirmation", "reschedule", "cancellation".
    context: free-text detail for the email template (e.g. appointment time).
    """
    payload = {
        "tenant_id": tenant_id,
        "customer_email": customer_email,
        "notification_type": notification_type,
        "context": context,
    }
    return n8n.trigger_notification(payload)


def trigger_outbound_reminder(
    customer_phone: str,
    reminder_reason: str,
    tenant_id: str = config.DEFAULT_TENANT_ID,
) -> dict:
    """Hand off an outbound proactive service-reminder call sequence to n8n.

    n8n owns scheduling the outbound call (e.g. via the Twilio/ElevenLabs
    outbound API) — this tool just queues the request with enough context.
    """
    payload = {
        "tenant_id": tenant_id,
        "customer_phone": customer_phone,
        "reminder_reason": reminder_reason,
    }
    return n8n.trigger_outbound_reminder(payload)
