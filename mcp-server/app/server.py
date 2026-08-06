"""FastMCP server entrypoint. Run locally with `python -m app.server`;
on Cloud Run this is what the Procfile's `web` process runs, listening on
$PORT with the streamable-http transport (Cloud Run only proxies HTTP, so
stdio transport isn't an option here).
"""
import os

from fastmcp import FastMCP

from app.logging_utils import logged
from app.tools.appointments import (
    book_appointment,
    cancel_appointment,
    check_availability,
    find_appointment,
    reschedule_appointment,
)
from app.tools.faq import dealership_faq_lookup
from app.tools.parts import check_part_availability
from app.tools.reminders import trigger_outbound_reminder
from app.tools.trade_in import intake_trade_in
from app.tools.vehicle_status import check_vehicle_status

mcp = FastMCP("dealership-voice-agent")

mcp.tool(logged(check_availability))
mcp.tool(logged(book_appointment))
mcp.tool(logged(reschedule_appointment))
mcp.tool(logged(cancel_appointment))
mcp.tool(logged(find_appointment))
mcp.tool(logged(intake_trade_in))
mcp.tool(logged(check_vehicle_status))
mcp.tool(logged(dealership_faq_lookup))
mcp.tool(logged(check_part_availability))
mcp.tool(logged(trigger_outbound_reminder))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
