# datasheetai/cli/main.py

import sys
import logging
import argparse

from datasheetai.config import load_config
from datasheetai.logging_config import setup_logging
from datasheetai.cli.commands.load_file import ingest_file
from datasheetai.cli.commands.query import query_db
from datasheetai.exceptions import DataSheetAIError

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Print results
# ------------------------------------------------------------------
def _print_results(results: list[dict]) -> None:
    # Handle empty result set
    if not results:
        print("No results found.")
        return

    columns = list(results[0].keys())

    # Calculate column widths from header and all row values
    col_widths = {col: len(col) for col in columns}
    for row in results:
        for col in columns:
            col_widths[col] = max(col_widths[col], len(str(row[col])))

    # Build format string: each column left-aligned within its calculated width
    row_fmt = " | ".join(f"{{:<{col_widths[col]}}}" for col in columns)
    separator = "-+-".join("-" * col_widths[col] for col in columns)

    print(row_fmt.format(*columns))
    print(separator)
    for row in results:
        print(row_fmt.format(*[str(row[col]) for col in columns]))

    print(f"\n{len(results)} row(s) returned.")

# ------------------------------------------------------------------
# CLI subcommand handlers
# ------------------------------------------------------------------
# Handle ingest subcommand - load a file into database
def _handle_ingest(args, config) -> int:
    logger.info(f"Ingest command: file='{args.path}', table='{args.table}', overwrite={args.overwrite}")
    result = ingest_file(
        path=args.path,
        table_name=args.table,
        config=config,
        overwrite=args.overwrite,
    )
    status = result["status"].upper()
    print(f"Success: Table '{result['table']}' {status} -> {result['rows']} row(s) loaded.")
    return 0

# Handle query subcommand — translate natural language query and return results
def _handle_query(args, config) -> int:
    logger.info(f"Query command: '{args.question}'")
    results = query_db(question=args.question, config=config)
    _print_results(results)
    return 0

# ------------------------------------------------------------------
# Argument parser
# ------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datasheetai",
        description="Natural language SQL query tool. Load data files and query them in plain English.",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        metavar="PATH",
        help="Path to config.yaml (default: config.yaml)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ingest subcommand
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Load a data file into the SQLite database.",
    )
    ingest_parser.add_argument("path", help="Path to the data file (.csv, .json, .xlsx)")
    ingest_parser.add_argument("table", help="Name of the destination table")
    ingest_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Drop and recreate the table if it already exists with a different schema",
    )

    # query subcommand
    query_parser = subparsers.add_parser(
        "query",
        help="Query the database using a natural language question.",
    )
    query_parser.add_argument("question", help="Natural language question, e.g. 'Show all employees earning over 80000'")

    return parser

# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------
def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    # Load config and set up logging before any module does real work
    config = load_config(args.config)
    setup_logging(config.logging)

    try:
        if args.command == "ingest":
            exit_code = _handle_ingest(args, config)
        elif args.command == "query":
            exit_code = _handle_query(args, config)
        else:
            parser.print_help()
            exit_code = 1
    except DataSheetAIError as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        exit_code = 1

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
