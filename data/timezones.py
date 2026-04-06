from PySide6.QtCore import QTimeZone

# All IANA timezone IDs that Qt recognises on this system — used for the search list
ALL_ZONES: list[str] = sorted(
    z.data().decode() for z in QTimeZone.availableTimeZoneIds()
)

# Curated popular timezones shown at the top of the add-clock dialog
POPULAR_ZONES: list[tuple[str, str]] = [
    ("Los Angeles",  "America/Los_Angeles"),
    ("Denver",       "America/Denver"),
    ("Chicago",      "America/Chicago"),
    ("New York",     "America/New_York"),
    ("São Paulo",    "America/Sao_Paulo"),
    ("London",       "Europe/London"),
    ("Paris",        "Europe/Paris"),
    ("Berlin",       "Europe/Berlin"),
    ("Stockholm",    "Europe/Stockholm"),
    ("Helsinki",     "Europe/Helsinki"),
    ("Moscow",       "Europe/Moscow"),
    ("Dubai",        "Asia/Dubai"),
    ("Mumbai",       "Asia/Kolkata"),
    ("Bangkok",      "Asia/Bangkok"),
    ("Singapore",    "Asia/Singapore"),
    ("Hong Kong",    "Asia/Hong_Kong"),
    ("Shanghai",     "Asia/Shanghai"),
    ("Tokyo",        "Asia/Tokyo"),
    ("Seoul",        "Asia/Seoul"),
    ("Sydney",       "Australia/Sydney"),
    ("Auckland",     "Pacific/Auckland"),
    ("UTC",          "UTC"),
]
