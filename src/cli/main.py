from __future__ import annotations
import argparse
import sys
from src.config.settings import get_settings
from src.db.connection import get_connection

def cmd_check_db() -> int:
    settings = get_settings()

    try:
        with get_connection(settings) as conn:
            with conn.cursor() as cur:
                cur.execute("select 1;")
                value = cur.fetchone()
    except Exception as exc:
        print(f"[FAIL] Database connection failed: {exc}", file=sys.stderr)
        return 1
    
    print(f"[OK] Database connection succeeded.  select 1 -> {value}")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dailyreport")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check-db", help="Verify DB connectivity and run SELECT 1")
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check-db":
        return cmd_check_db()
    
    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())