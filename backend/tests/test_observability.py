from app.observability import summarize_payload, summarize_text


def test_summarize_text_truncates_long_content():
    text = "secret-value-" + ("x" * 160)

    summary = summarize_text(text, limit=32)

    assert summary.endswith("(len=173)")
    assert text not in summary


def test_summarize_payload_redacts_sensitive_keys():
    summary = summarize_payload({"api_key": "sk-secret", "content": "hello"})

    assert "sk-secret" not in summary
    assert "[REDACTED]" in summary
    assert "hello" in summary
