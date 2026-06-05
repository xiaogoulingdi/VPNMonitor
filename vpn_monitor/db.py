import sqlite3
from pathlib import Path

from .config import settings
from .models import Event


EVENT_COLUMNS = [
    "ts", "time_utc", "source_ip", "source_port", "action", "network",
    "destination", "domain", "dest_port", "inbound", "outbound", "email",
    "category", "is_internal", "raw", "raw_hash", "created_at",
]


def connect_db(db_path: Path | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or settings.db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db() -> None:
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER NOT NULL,
                time_utc TEXT NOT NULL,
                source_ip TEXT,
                source_port INTEGER,
                action TEXT,
                network TEXT,
                destination TEXT,
                domain TEXT,
                dest_port INTEGER,
                inbound TEXT,
                outbound TEXT,
                email TEXT,
                category TEXT,
                is_internal INTEGER NOT NULL DEFAULT 0,
                raw TEXT NOT NULL,
                raw_hash TEXT NOT NULL UNIQUE,
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS collector_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
            CREATE INDEX IF NOT EXISTS idx_events_domain ON events(domain);
            CREATE INDEX IF NOT EXISTS idx_events_destination ON events(destination);
            CREATE INDEX IF NOT EXISTS idx_events_email ON events(email);
            CREATE INDEX IF NOT EXISTS idx_events_inbound ON events(inbound);
            CREATE INDEX IF NOT EXISTS idx_events_source_ip ON events(source_ip);
            CREATE INDEX IF NOT EXISTS idx_events_internal ON events(is_internal);
            """
        )


def get_state(conn: sqlite3.Connection, key: str, default: str = "0") -> str:
    row = conn.execute("SELECT value FROM collector_state WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set_state(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO collector_state(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def insert_event(conn: sqlite3.Connection, event: Event) -> None:
    data = event.as_db_dict()
    placeholders = ",".join(["?"] * len(EVENT_COLUMNS))
    conn.execute(
        f"INSERT OR IGNORE INTO events ({','.join(EVENT_COLUMNS)}) VALUES ({placeholders})",
        [data[column] for column in EVENT_COLUMNS],
    )
