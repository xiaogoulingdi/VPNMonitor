import time

from vpn_monitor.config import settings
from vpn_monitor.db import connect_db


def now_ts() -> int:
    return int(time.time())


def safe_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def first(params, key: str, default: str = "") -> str:
    if hasattr(params, "getlist"):
        values = params.getlist(key)
        return values[0] if values else default
    value = params.get(key, [default])
    if isinstance(value, list):
        return value[0] if value else default
    return value if value is not None else default


def build_filters(params) -> tuple[str, list]:
    clauses = []
    args = []
    from_ts = safe_int(first(params, "from_ts"))
    to_ts = safe_int(first(params, "to_ts"))
    email = first(params, "email")
    inbound = first(params, "inbound")
    source_ip = first(params, "source_ip")
    domain = first(params, "domain")
    category = first(params, "category")
    include_internal = first(params, "include_internal") == "1"
    if from_ts:
        clauses.append("ts >= ?"); args.append(from_ts)
    if to_ts:
        clauses.append("ts <= ?"); args.append(to_ts)
    if email:
        clauses.append("email = ?"); args.append(email)
    if inbound:
        clauses.append("inbound = ?"); args.append(inbound)
    if source_ip:
        clauses.append("source_ip = ?"); args.append(source_ip)
    if domain:
        clauses.append("(domain LIKE ? OR destination LIKE ?)"); args.extend([f"%{domain.lower()}%", f"%{domain.lower()}%"])
    if category:
        clauses.append("category = ?"); args.append(category)
    if not include_internal:
        clauses.append("is_internal = 0")
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    return where, args


def row_to_event_dict(row) -> dict:
    data = dict(row)
    data["display_target"] = data.get("domain") or data.get("destination") or ""
    return data


def query_summary(params) -> dict:
    where, args = build_filters(params)
    with connect_db() as conn:
        totals = conn.execute(f"SELECT COUNT(*) AS events, COUNT(DISTINCT COALESCE(NULLIF(domain, ''), destination)) AS targets, COUNT(DISTINCT NULLIF(email, '')) AS users, COUNT(DISTINCT source_ip) AS sources, MAX(ts) AS last_ts FROM events {where}", args).fetchone()
        top_domains = [dict(row) for row in conn.execute(f"SELECT COALESCE(NULLIF(domain, ''), destination) AS target, COUNT(*) AS count FROM events {where} GROUP BY target ORDER BY count DESC LIMIT 20", args)]
        top_users = [dict(row) for row in conn.execute(f"SELECT COALESCE(NULLIF(email, ''), 'unknown') AS user, COUNT(*) AS count FROM events {where} GROUP BY user ORDER BY count DESC LIMIT 12", args)]
        inbounds = [dict(row) for row in conn.execute(f"SELECT COALESCE(NULLIF(inbound, ''), 'unknown') AS inbound, COUNT(*) AS count FROM events {where} GROUP BY inbound ORDER BY count DESC LIMIT 12", args)]
        categories = [dict(row) for row in conn.execute(f"SELECT category, COUNT(*) AS count FROM events {where} GROUP BY category ORDER BY count DESC", args)]
        hourly = [dict(row) for row in conn.execute(f"SELECT CAST(ts / 3600 AS INTEGER) * 3600 AS bucket, COUNT(*) AS count FROM events {where} GROUP BY bucket ORDER BY bucket ASC LIMIT 240", args)]
    return {"totals": dict(totals), "top_domains": top_domains, "top_users": top_users, "inbounds": inbounds, "categories": categories, "hourly": hourly, "retention_days": settings.retention_days, "access_log": str(settings.access_log)}


def query_events(params) -> list[dict]:
    where, args = build_filters(params)
    limit = min(max(safe_int(first(params, "limit")) or 200, 1), 1000)
    offset = max(safe_int(first(params, "offset")) or 0, 0)
    with connect_db() as conn:
        rows = conn.execute(f"SELECT * FROM events {where} ORDER BY ts DESC, id DESC LIMIT ? OFFSET ?", [*args, limit, offset]).fetchall()
    return [row_to_event_dict(row) for row in rows]


def query_active(params) -> list[dict]:
    scoped = dict(params)
    scoped["from_ts"] = [str(now_ts() - settings.active_window_seconds)]
    scoped["include_internal"] = ["0"]
    where, args = build_filters(scoped)
    with connect_db() as conn:
        rows = conn.execute(f"SELECT COALESCE(NULLIF(email, ''), 'unknown') AS user, source_ip, inbound, COALESCE(NULLIF(domain, ''), destination) AS target, dest_port, network, category, MAX(ts) AS last_ts, COUNT(*) AS count FROM events {where} GROUP BY user, source_ip, inbound, target, dest_port, network, category ORDER BY last_ts DESC, count DESC LIMIT 30", args).fetchall()
    return [dict(row) for row in rows]


def query_options() -> dict:
    with connect_db() as conn:
        emails = [row[0] for row in conn.execute("SELECT DISTINCT email FROM events WHERE email != '' ORDER BY email")]
        inbounds = [row[0] for row in conn.execute("SELECT DISTINCT inbound FROM events WHERE inbound != '' ORDER BY inbound")]
        sources = [row[0] for row in conn.execute("SELECT DISTINCT source_ip FROM events WHERE source_ip != '' ORDER BY source_ip")]
    return {"emails": emails, "inbounds": inbounds, "sources": sources, "categories": ["overseas", "domestic", "ip", "other", "internal"]}


def export_rows(params) -> list[dict]:
    scoped = dict(params)
    scoped["limit"] = ["100000"]
    scoped["offset"] = ["0"]
    return query_events(scoped)
