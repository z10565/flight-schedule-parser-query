"""Row validation: airport list loading, single-row checks, record building."""

import math
import re
from datetime import datetime

_FLIGHT_ID_RE = re.compile(r"[A-Za-z0-9]{2,8}\Z")
_AIRPORT_RE = re.compile(r"[A-Z]{3}\Z")
_DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}\Z")
_DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def load_airports(path: str) -> set[str]:
    """Read airport codes, ignoring blank lines and comments."""
    airports = set()
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            code = line.strip()
            if code and not code.startswith("#"):
                airports.add(code)
    return airports


def _valid_datetime(value: str) -> bool:
    """Check exact formatting and whether the date/time really exists."""
    if not _DATETIME_RE.fullmatch(value):
        return False
    try:
        parsed = datetime.strptime(value, _DATETIME_FORMAT)
    except ValueError:
        return False
    return parsed.strftime(_DATETIME_FORMAT) == value


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Return the first failing validation code, or None for a valid row."""
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    values = [field.strip() for field in fields]
    if any(value == "" for value in values):
        return "MISSING_FIELD"

    flight_id, origin, destination, departure, arrival, price_text = values

    if not _FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"
    if not _AIRPORT_RE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"
    if not _AIRPORT_RE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"
    if not _valid_datetime(departure):
        return "INVALID_DEPARTURE"
    if not _valid_datetime(arrival):
        return "INVALID_ARRIVAL"

    departure_dt = datetime.strptime(departure, _DATETIME_FORMAT)
    arrival_dt = datetime.strptime(arrival, _DATETIME_FORMAT)
    if arrival_dt <= departure_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price = float(price_text)
    except (TypeError, ValueError):
        return "INVALID_PRICE"
    if not math.isfinite(price):
        return "INVALID_PRICE"
    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Convert a valid row into the required flight record."""
    values = [field.strip() for field in fields]
    return {
        "flight_id": values[0],
        "origin": values[1],
        "destination": values[2],
        "departure_datetime": values[3],
        "arrival_datetime": values[4],
        "price": float(values[5]),
    }
