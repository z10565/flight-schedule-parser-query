"""Reading CSV files into flight records and error messages."""

import csv
from pathlib import Path

from validator import validate_row, to_record


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process CSV files and detect duplicates across the complete input set."""
    records = []
    errors = []
    seen_flights = set()

    for path in paths:
        file_path = Path(path)
        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            for line_number, fields in enumerate(reader, start=1):
                # The first physical CSV record is the header.
                if line_number == 1:
                    continue

                # csv.reader returns [] for a physically blank line. For comment lines, inspect the original source line as comments aren't CSV.
                # The specification defines line-based records; read comments by handling them before csv parsing in the common one-line case.
                stripped_fields = [field.strip() for field in fields]
                if not fields or (len(fields) == 1 and fields[0].strip() == ""):
                    continue
                if len(fields) == 1 and fields[0].lstrip().startswith("#"):
                    continue

                error_code = validate_row(stripped_fields, airports)
                if error_code is None:
                    record = to_record(stripped_fields)
                    duplicate_key = (record["flight_id"], record["departure_datetime"])
                    if duplicate_key in seen_flights:
                        error_code = "DUPLICATE_FLIGHT"
                    else:
                        seen_flights.add(duplicate_key)
                        records.append(record)

                if error_code is not None:
                    free_text = ",".join(fields)
                    errors.append(
                        f"{file_path.name}:{line_number}: {error_code} | {free_text}"
                    )

    return records, errors
