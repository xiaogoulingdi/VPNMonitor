import sqlite3

from vpn_monitor.config import settings


def query_marzban_users() -> list[dict]:
    if not settings.marzban_db_path.exists():
        return []
    try:
        conn = sqlite3.connect(f"file:{settings.marzban_db_path}?mode=ro", uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, username, status, used_traffic, data_limit, expire, online_at
            FROM users
            ORDER BY id
            """
        ).fetchall()
    except sqlite3.Error:
        return []
    finally:
        try:
            conn.close()
        except UnboundLocalError:
            pass
    users = []
    for row in rows:
        data = dict(row)
        data["email"] = f"{data['id']}.{data['username']}"
        users.append(data)
    return users
