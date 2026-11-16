"""Running queries against the flight database."""

import math
import re
from datetime import datetime

_RECORD_KEYS = {
    "flight_id", "origin", "destination", "departure_datetime",
    "arrival_datetime", "price",
}
_ALLOWED_KEYS = _RECORD_KEYS | {"min_price", "sort_by", "order", "limit"}
_DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}\Z")
_DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def _valid_datetime(value) -> bool:
    if not isinstance(value, str) or not _DATETIME_RE.fullmatch(value):
        return False
    try:
        parsed = datetime.strptime(value, _DATETIME_FORMAT)
    except ValueError:
        return False
    return parsed.strftime(_DATETIME_FORMAT) == value


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _valid_query(query) -> bool:
    if not isinstance(query, dict) or any(key not in _ALLOWED_KEYS for key in query):
        return False

    for key in ("flight_id", "origin", "destination"):
        if key in query and not isinstance(query[key], str):
            return False

    for key in ("departure_datetime", "arrival_datetime"):
        if key in query and not _valid_datetime(query[key]):
            return False

    for key in ("price", "min_price"):
        if key in query and not _is_number(query[key]):
            return False

    if "sort_by" in query and (not isinstance(query["sort_by"], str) or query["sort_by"] not in _RECORD_KEYS):
        return False
    if "order" in query and ("sort_by" not in query or query["order"] not in ("asc", "desc")):
        return False
    if "limit" in query:
        limit = query["limit"]
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for a query."""
    if not _valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = []
    for flight in db:
        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            continue
        if "origin" in query and flight["origin"] != query["origin"]:
            continue
        if "destination" in query and flight["destination"] != query["destination"]:
            continue
        if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
            continue
        if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
            continue
        if "price" in query and flight["price"] > query["price"]:
            continue
        if "min_price" in query and flight["price"] < query["min_price"]:
            continue
        matches.append(flight)

    if "sort_by" in query:
        matches = sorted(matches, key=lambda flight: flight[query["sort_by"]], reverse=query.get("order", "asc") == "desc")
    if "limit" in query:
        matches = matches[:query["limit"]]
    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list and always return a list."""
    if isinstance(queries, list):
        return [run_query(db, query) for query in queries]
    return [run_query(db, queries)]
