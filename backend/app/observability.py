import json
import logging
from typing import Any


SENSITIVE_KEY_PARTS = ("api_key", "authorization", "password", "secret", "token")
LOG_FORMAT = "%(levelname)s:%(name)s:%(message)s"


def configure_app_logging() -> None:
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    if not app_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        app_logger.addHandler(handler)
    app_logger.propagate = True


def summarize_text(text: str, limit: int = 120) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit]}...(len={len(normalized)})"


def summarize_payload(payload: Any, limit: int = 240) -> str:
    redacted = _redact(payload)
    try:
        text = json.dumps(redacted, ensure_ascii=False, sort_keys=True)
    except TypeError:
        text = str(redacted)
    return summarize_text(text, limit=limit)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if _is_sensitive_key(str(key)) else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)
