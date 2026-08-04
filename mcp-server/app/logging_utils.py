"""Tool-call logging wrapper.

Cloud Run captures stdout/stderr automatically, but FastMCP's default
streamable-http server doesn't emit per-request access logs — so a 200
response tells you the transport worked, not whether the tool underneath it
actually did anything. This wraps every registered tool so the exact
arguments and outcome of each call show up in Cloud Run logs, which is what
you actually need when a client (like an LLM-driven agent) calls a tool
with the wrong argument names or a call fails partway through.
"""
import functools
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("dealership-mcp")


def logged(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        logger.info("tool_call name=%s args=%r", fn.__name__, kwargs)
        try:
            result = fn(*args, **kwargs)
            logger.info("tool_ok name=%s result=%r", fn.__name__, result)
            return result
        except Exception:
            logger.exception("tool_error name=%s", fn.__name__)
            raise

    return wrapper
