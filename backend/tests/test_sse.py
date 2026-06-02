import json

from app.chat.sse import format_sse


def test_format_sse_returns_json_data_line():
    payload = format_sse({"type": "delta", "messageId": "m1", "content": "hello"})

    assert payload.startswith("data: ")
    assert payload.endswith("\n\n")
    decoded = json.loads(payload.removeprefix("data: ").strip())
    assert decoded == {"type": "delta", "messageId": "m1", "content": "hello"}
