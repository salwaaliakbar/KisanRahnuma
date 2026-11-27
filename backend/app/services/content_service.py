"""Read/write access to the admin-editable JSON files in app/data.

Keeps those files as the single source of truth (no parallel database copy). A write
takes effect immediately: `ConversationService` builds a fresh `CropService`,
`CreditService`, etc. on every request (see `app/api/chat.py`), and each reloads through
`data_loader.load_json`, so clearing that cache is all that's needed - no restart.
"""
import json
from typing import Any

from fastapi import HTTPException

from app.services.data_loader import DATA_DIR, load_json

EDITABLE_FILES = {"crop_rates.json", "credit_info.json", "certifications.json", "knowledge_base.json"}


def read(filename: str) -> Any:
    if filename not in EDITABLE_FILES:
        raise HTTPException(status_code=404, detail="Unknown content file")
    return load_json(filename)


def write(filename: str, data: Any) -> None:
    if filename not in EDITABLE_FILES:
        raise HTTPException(status_code=404, detail="Unknown content file")
    try:
        text = json.dumps(data, ensure_ascii=False, indent=2)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Not valid JSON: {exc}") from None
    (DATA_DIR / filename).write_text(text, encoding="utf-8")
    load_json.cache_clear()
