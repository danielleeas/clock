import json
from pathlib import Path
from typing import List, Dict

_CLOCKS_FILE = Path.home() / ".worldclock" / "clocks.json"

_DEFAULTS: List[Dict[str, str]] = [
    {"label": "New York",  "tz_id": "America/New_York"},
    {"label": "London",    "tz_id": "Europe/London"},
    {"label": "Stockholm", "tz_id": "Europe/Stockholm"},
    {"label": "Dubai",     "tz_id": "Asia/Dubai"},
    {"label": "Tokyo",     "tz_id": "Asia/Tokyo"},
    {"label": "Sydney",    "tz_id": "Australia/Sydney"},
]


def load_clocks() -> List[Dict[str, str]]:
    """Return list of {"label": str, "tz_id": str} dicts."""
    if _CLOCKS_FILE.exists():
        try:
            data = json.loads(_CLOCKS_FILE.read_text())
            if isinstance(data, list) and all("tz_id" in d for d in data):
                return data
        except Exception:
            pass
    return list(_DEFAULTS)


def save_clocks(clocks: List[Dict[str, str]]) -> None:
    _CLOCKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CLOCKS_FILE.write_text(json.dumps(clocks, indent=2))
