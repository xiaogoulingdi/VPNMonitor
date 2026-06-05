#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export MONITOR_HOST="${MONITOR_HOST:-127.0.0.1}"
export MONITOR_PORT="${MONITOR_PORT:-19100}"
export MONITOR_COOKIE_PATH="${MONITOR_COOKIE_PATH:-/}"
export MONITOR_COLLECTOR_ENABLED="${MONITOR_COLLECTOR_ENABLED:-false}"

exec .venv/bin/uvicorn vpn_monitor.web.app:app --host "$MONITOR_HOST" --port "$MONITOR_PORT" --reload
