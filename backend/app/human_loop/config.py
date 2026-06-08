from typing import Any


WRITE_APPROVAL_TOOLS = ("write_file", "edit_file")


def build_interrupt_on() -> dict[str, dict[str, Any]]:
    return {
        tool_name: {
            "allowed_decisions": ["approve", "reject"],
            "description": f"Human approval is required before running {tool_name}.",
        }
        for tool_name in WRITE_APPROVAL_TOOLS
    }
