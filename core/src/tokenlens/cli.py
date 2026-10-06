import argparse
import json
import sys
import sqlite3
from .contract import InvalidEvent, validate
from .store import Store

def main():
    p = argparse.ArgumentParser(description="TokenLens: ingestao de eventos normalizados, nunca logs brutos.")
    p.add_argument("command", choices=["validate", "ingest"])
    p.add_argument("--db", default="telemetry/tokenlens.sqlite3")
    args = p.parse_args()
    try:
        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise InvalidEvent()
        event = validate(json.loads(raw))
        if args.command == "ingest":
            Store(args.db).put(event)
        print("Evento valido.")
    except (ValueError, TypeError, KeyError, OSError, RecursionError, sqlite3.Error):
        print("Evento rejeitado; conteudo omitido.", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
