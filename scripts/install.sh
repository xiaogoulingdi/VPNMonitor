#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${VPN_MONITOR_REPO_URL:-https://github.com/xiaogoulingdi/VPNMonitor/archive/refs/heads/main.tar.gz}"
INSTALL_DIR="${VPN_MONITOR_INSTALL_DIR:-/opt/vpn-monitor}"
ENV_FILE="${VPN_MONITOR_ENV_FILE:-/etc/vpn-monitor.env}"
LOGIN_FILE="${VPN_MONITOR_LOGIN_FILE:-/root/vpn-monitor-login.txt}"
SERVICE_FILE="${VPN_MONITOR_SERVICE_FILE:-/etc/systemd/system/vpn-monitor.service}"
SERVICE_NAME="${VPN_MONITOR_SERVICE_NAME:-vpn-monitor.service}"
HOST="${VPN_MONITOR_HOST:-127.0.0.1}"
PORT="${VPN_MONITOR_PORT:-9100}"
BASE_PATH="${VPN_MONITOR_BASE_PATH:-/monitor}"
DB_PATH="${VPN_MONITOR_DB:-/var/lib/vpn-monitor/monitor.db}"
XRAY_ACCESS_LOG="${XRAY_ACCESS_LOG:-/var/lib/marzban/xray_access.log}"
RETENTION_DAYS="${VPN_MONITOR_RETENTION_DAYS:-30}"
POLL_SECONDS="${VPN_MONITOR_POLL_SECONDS:-1.5}"
ACTIVE_WINDOW_SECONDS="${VPN_MONITOR_ACTIVE_WINDOW_SECONDS:-600}"
USERNAME="${VPN_MONITOR_USERNAME:-monitor}"

if [ "${VPN_MONITOR_PUBLIC:-0}" = "1" ]; then
  HOST="0.0.0.0"
fi

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "Please run as root." >&2
  exit 1
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || return 1
}

install_packages() {
  if need_cmd apt-get; then
    apt-get update
    apt-get install -y ca-certificates curl tar openssl python3 python3-venv
    if ! python3 -m venv "$tmpdir/venv-check" >/dev/null 2>&1; then
      rm -rf "$tmpdir/venv-check"
      local pyver
      pyver="$(python3 - <<'PY' 2>/dev/null || true
import sys
print(f"python{sys.version_info.major}.{sys.version_info.minor}-venv")
PY
)"
      if [ -n "$pyver" ]; then
        apt-get install -y "$pyver"
      fi
    fi
    rm -rf "$tmpdir/venv-check"
  elif need_cmd dnf; then
    dnf install -y ca-certificates curl tar openssl python3 python3-pip
  elif need_cmd yum; then
    yum install -y ca-certificates curl tar openssl python3 python3-pip
  else
    echo "Unsupported package manager. Please install Python 3, venv, curl, tar, and openssl first." >&2
    exit 1
  fi
}

make_password_hash() {
  local password="$1"
  python3 - "$password" <<'PY'
import hashlib
import sys
print(hashlib.sha256(sys.argv[1].encode()).hexdigest())
PY
}

install_packages

echo "Downloading VPN Monitor..."
curl -fsSL "$REPO_URL" -o "$tmpdir/source.tar.gz"
tar -xzf "$tmpdir/source.tar.gz" -C "$tmpdir"
src="$(find "$tmpdir" -maxdepth 2 -type d -name vpn_monitor -printf '%h\n' | head -1)"
if [ -z "$src" ]; then
  echo "Could not find vpn_monitor package in archive." >&2
  exit 1
fi

echo "Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR" "$(dirname "$DB_PATH")"
rsync_available=0
if need_cmd rsync; then
  rsync_available=1
fi
if [ "$rsync_available" = "1" ]; then
  rsync -a --delete \
    --exclude '.git' --exclude '.venv' --exclude '__pycache__' --exclude '*.pyc' \
    "$src"/ "$INSTALL_DIR"/
else
  find "$INSTALL_DIR" -mindepth 1 -maxdepth 1 ! -name monitor.db -exec rm -rf {} +
  cp -a "$src"/. "$INSTALL_DIR"/
fi

echo "Creating virtual environment..."
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/python" -m pip install --upgrade pip
"$INSTALL_DIR/.venv/bin/python" -m pip install -r "$INSTALL_DIR/requirements.txt"

password="${VPN_MONITOR_PASSWORD:-$(openssl rand -base64 18 | tr -d '\n')}"
password_hash="$(make_password_hash "$password")"
session_secret="${VPN_MONITOR_SESSION_SECRET:-$(openssl rand -hex 32)}"

cat > "$ENV_FILE" <<EOF
MONITOR_USERNAME=$USERNAME
MONITOR_PASSWORD_SHA256=$password_hash
MONITOR_SESSION_SECRET=$session_secret
MONITOR_HOST=$HOST
MONITOR_PORT=$PORT
MONITOR_DB=$DB_PATH
XRAY_ACCESS_LOG=$XRAY_ACCESS_LOG
MONITOR_RETENTION_DAYS=$RETENTION_DAYS
MONITOR_POLL_SECONDS=$POLL_SECONDS
MONITOR_ACTIVE_WINDOW_SECONDS=$ACTIVE_WINDOW_SECONDS
MONITOR_COOKIE_PATH=$BASE_PATH
MONITOR_COLLECTOR_ENABLED=true
EOF
chmod 600 "$ENV_FILE"

cat > "$LOGIN_FILE" <<EOF
VPN Monitor login

URL:
  http://<your-server-ip>:$PORT/
  or your reverse proxy path, for example /monitor/

Username: $USERNAME
Password: $password

Env file: $ENV_FILE
Installed at: $INSTALL_DIR
EOF
chmod 600 "$LOGIN_FILE"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=VPN Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$INSTALL_DIR/.venv/bin/uvicorn vpn_monitor.web.app:app --host $HOST --port $PORT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME" >/dev/null
systemctl restart "$SERVICE_NAME"

echo
echo "VPN Monitor installed."
echo "Service: $SERVICE_NAME"
echo "Listen: http://$HOST:$PORT"
echo "Credentials saved to: $LOGIN_FILE"
echo
echo "If you use Nginx with /monitor/, add the snippet from:"
echo "  $INSTALL_DIR/examples/nginx-monitor.example.conf"
echo
systemctl --no-pager --full status "$SERVICE_NAME" | sed -n '1,12p'
