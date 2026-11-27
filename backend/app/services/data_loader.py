"""Loads the dummy JSON data files from app/data (cached after first read)."""
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache
def load_json(filename: str) -> Any:
    with (DATA_DIR / filename).open(encoding="utf-8") as f:
        return json.load(f)
