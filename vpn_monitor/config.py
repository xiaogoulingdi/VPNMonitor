from dataclasses import dataclass
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    db_path: Path = Path(os.environ.get("MONITOR_DB", BASE_DIR / "monitor.db"))
    access_log: Path = Path(os.environ.get("XRAY_ACCESS_LOG", "/var/lib/marzban/xray_access.log"))
    host: str = os.environ.get("MONITOR_HOST", "127.0.0.1")
    port: int = int(os.environ.get("MONITOR_PORT", "9100"))
    retention_days: int = int(os.environ.get("MONITOR_RETENTION_DAYS", "30"))
    poll_seconds: float = float(os.environ.get("MONITOR_POLL_SECONDS", "1.5"))
    active_window_seconds: int = int(os.environ.get("MONITOR_ACTIVE_WINDOW_SECONDS", "600"))
    username: str = os.environ.get("MONITOR_USERNAME", "monitor")
    password_sha256: str = os.environ.get("MONITOR_PASSWORD_SHA256", "")
    session_secret: str = os.environ.get("MONITOR_SESSION_SECRET", "")
    session_ttl_seconds: int = int(os.environ.get("MONITOR_SESSION_TTL_SECONDS", "43200"))
    cookie_name: str = os.environ.get("MONITOR_COOKIE_NAME", "vpn_monitor_session")
    cookie_path: str = os.environ.get("MONITOR_COOKIE_PATH", "/monitor")
    collector_enabled: bool = env_bool("MONITOR_COLLECTOR_ENABLED", True)


settings = Settings()
