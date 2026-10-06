import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .contract import validate

class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, synthetic INTEGER NOT NULL, payload TEXT NOT NULL)")
            db.execute("CREATE INDEX IF NOT EXISTS events_time ON events(timestamp)")

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            with db:
                yield db
        finally:
            db.close()

    def put(self, event):
        validate(event)
        with self.connect() as db:
            return db.execute("INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?)", (event["event_id"], event["timestamp"], int(event["synthetic"]), json.dumps(event, ensure_ascii=True))).rowcount

    def events(self, synthetic=False):
        with self.connect() as db:
            rows = db.execute("SELECT payload FROM events WHERE synthetic=? ORDER BY timestamp DESC", (int(synthetic),)).fetchall()
        return [validate(json.loads(row[0])) for row in rows]

    def snapshot(self, event):
        validate(event)
        if event["scope"] != "context_snapshot":
            raise ValueError("Somente snapshots podem ser substituidos.")
        with self.connect() as db:
            old = db.execute("SELECT payload FROM events WHERE event_id=?", (event["event_id"],)).fetchone()
            if old:
                previous = validate(json.loads(old[0]))
                if previous["scope"] != "context_snapshot" or previous["provider"] != event["provider"] or previous["synthetic"] != event["synthetic"]:
                    raise ValueError("Identificador em uso.")
                event["task"] = previous["task"]
            db.execute("INSERT INTO events VALUES (?, ?, ?, ?) ON CONFLICT(event_id) DO UPDATE SET timestamp=excluded.timestamp, payload=excluded.payload", (event["event_id"], event["timestamp"], int(event["synthetic"]), json.dumps(event)))

    def label(self, event_id, category, complexity):
        with self.connect() as db:
            row = db.execute("SELECT payload FROM events WHERE event_id=?", (event_id,)).fetchone()
            if row is None:
                return False
            e = json.loads(row[0])
            e["task"] = {"category": category, "complexity": complexity, "classification_source": "manual"}
            validate(e)
            db.execute("UPDATE events SET payload=? WHERE event_id=?", (json.dumps(e), event_id))
            return True
