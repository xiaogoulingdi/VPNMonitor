from pathlib import Path
import threading
import time

from vpn_monitor.adapters.base import BaseLogAdapter
from vpn_monitor.adapters.xray_access_log import XrayAccessLogAdapter
from vpn_monitor.config import settings
from vpn_monitor.db import connect_db, get_state, insert_event, set_state


def prune_old_events(conn) -> None:
    if settings.retention_days <= 0:
        return
    cutoff = int(time.time()) - settings.retention_days * 86400
    conn.execute("DELETE FROM events WHERE ts < ?", (cutoff,))


def ingest_once(access_log: Path | None = None, adapter: BaseLogAdapter | None = None) -> int:
    log_path = access_log or settings.access_log
    adapter = adapter or XrayAccessLogAdapter()
    if not log_path.exists():
        return 0

    with connect_db() as conn:
        stat = log_path.stat()
        inode = str(stat.st_ino)
        last_inode = get_state(conn, "access_inode", "")
        offset = int(get_state(conn, "access_offset", "0"))
        if last_inode != inode or stat.st_size < offset:
            offset = 0

        inserted = 0
        with log_path.open("r", encoding="utf-8", errors="replace") as fh:
            fh.seek(offset)
            for line in fh:
                event = adapter.parse_line(line)
                if event:
                    before = conn.total_changes
                    insert_event(conn, event)
                    if conn.total_changes > before:
                        inserted += 1
            offset = fh.tell()

        set_state(conn, "access_inode", inode)
        set_state(conn, "access_offset", str(offset))
        prune_old_events(conn)
        return inserted


def collector_loop(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            ingest_once()
        except Exception as exc:
            print(f"[collector] {exc}", flush=True)
        stop_event.wait(settings.poll_seconds)
