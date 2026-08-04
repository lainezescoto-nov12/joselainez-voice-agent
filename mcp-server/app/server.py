"""FastMCP server entrypoint. Run locally with `python -m app.server`;
on Cloud Run this is what the Procfile's `web` process runs, listening on
$PORT with the streamable-http transport (Cloud Run only proxies HTTP, so
stdio transport isn't an option here).
"""
import os

from fastmcp import FastMCP

from app.tools.appointments import (
    book_appointment,
    cancel_appointment,
    check_availability,
    find_appointment,
    reschedule_appointment,
)
from app.tools.faq import dealership_faq_lookup
from app.tools.notifications import trigger_notification, trigger_outbound_reminder
from app.tools.trade_in import intake_trade_in
from app.tools.vehicle_status import check_vehicle_status

mcp = FastMCP("dealership-voice-agent")

mcp.tool(check_availability)
mcp.tool(book_appointment)
mcp.tool(reschedule_appointment)
mcp.tool(cancel_appointment)
mcp.tool(find_appointment)
mcp.tool(intake_trade_in)
mcp.tool(check_vehicle_status)
mcp.tool(dealership_faq_lookup)
mcp.tool(trigger_notification)
mcp.tool(trigger_outbound_reminder)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
