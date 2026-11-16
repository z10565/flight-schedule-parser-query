"""Flight Schedule Parser and Query Tool - command-line entry point."""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251ADB103"
FIRST_NAME = "Zarina"
LAST_NAME = "Alliyarova"


def _write_json(path: Path, data) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")


def main(argv: list[str] | None = None) -> int:
    """Run the program and return an exit code (0, 1 or 2)."""
    parser = argparse.ArgumentParser(description="Flight schedule parser and query tool")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="Parse one CSV file")
    source.add_argument("-d", metavar="FOLDER", help="Parse all CSV files in a folder")
    source.add_argument("-j", metavar="FILE", help="Load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", help="Airport list (required with -i or -d)")
    parser.add_argument("-o", metavar="FILE", help="Output database JSON path")
    parser.add_argument("-q", metavar="FILE", help="JSON query file")
    parser.add_argument("-r", metavar="FOLDER", default=".", help="Query response folder")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    csv_mode = args.i is not None or args.d is not None
    if csv_mode and not args.a:
        parser.error("-a is required with -i or -d")
    if args.j and args.o:
        parser.error("-o cannot be used with -j")

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = None

    try:
        if args.j:
            with open(args.j, "r", encoding="utf-8") as file:
                db = json.load(file)
            if not isinstance(db, list) or any(not isinstance(item, dict) for item in db):
                raise ValueError("JSON database must be an array of objects")
        else:
            if args.i:
                paths = [args.i]
            else:
                folder = Path(args.d)
                paths = sorted(
                    str(path) for path in folder.iterdir()
                    if path.is_file() and path.name.endswith(".csv")
                )
                if not paths:
                    raise FileNotFoundError("No .csv files found in the folder")

            airports = load_airports(args.a)
            db, errors = parse_files(paths, airports)

            output_path = Path(args.o) if args.o else Path("db.json")
            _write_json(output_path, db)

            log_path = output_path.parent / "errors.log"
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            ))
            logger.addHandler(handler)
            for error in errors:
                logger.warning(error)

        if args.q:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)
            if not isinstance(queries, (dict, list)):
                raise ValueError("Query JSON must contain an object or an array")

            response = run_queries(db, queries)
            response_folder = Path(args.r)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
            _write_json(response_folder / filename, response)

        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())
