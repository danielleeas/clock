import json
from dataclasses import dataclass, asdict, field
from pathlib import Path

_SETTINGS_FILE = Path.home() / ".worldclock" / "settings.json"


@dataclass
class AppSettings:
    use_24h: bool = True
    show_seconds: bool = True
    grid_view: bool = True

    def save(self) -> None:
        _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _SETTINGS_FILE.write_text(json.dumps(asdict(self), indent=2))

    @classmethod
    def load(cls) -> "AppSettings":
        if _SETTINGS_FILE.exists():
            try:
                data = json.loads(_SETTINGS_FILE.read_text())
                valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
                return cls(**valid)
            except Exception:
                pass
        return cls()
