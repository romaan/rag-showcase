import logging
import json
from app.config import settings

def setup_logging():
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(message)s")

def log_event(event: str, **kwargs):
    payload = {"event": event, **kwargs}
    logging.getLogger("rag").info(json.dumps(payload, ensure_ascii=False))
