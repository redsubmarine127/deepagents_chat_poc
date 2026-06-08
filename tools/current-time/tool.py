from datetime import UTC, datetime

from langchain_core.tools import tool


@tool
def current_time() -> str:
    """Return the current UTC time in ISO format."""
    return datetime.now(UTC).isoformat()


def get_tool():
    return current_time
