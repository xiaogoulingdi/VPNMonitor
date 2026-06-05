# VPN Monitor

[简体中文](../README.md) | English | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md)

VPN Monitor is a lightweight domain-level traffic monitor for personal VPN nodes. The first version supports Xray access logs and stores normalized events in SQLite.

It does not decrypt HTTPS traffic. It only records metadata already visible in proxy logs, such as time, source IP, destination domain/IP, inbound tag, user/device, network protocol, and category.

## Features

- FastAPI web app with Jinja2 templates and vanilla JavaScript/CSS.
- Application login with signed HTTP-only cookies.
- Xray access log adapter and normalized event model.
- SQLite storage using the Python standard library.
- Summary cards, active access, top domains, user/device stats, hourly trend, recent events, and CSV/JSON export.
- Adapter-oriented structure for future data sources.

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp examples/vpn-monitor.env.example /etc/vpn-monitor.env
chmod 600 /etc/vpn-monitor.env
```

Generate a password hash and session secret:

```bash
python3 - <<'PY'
import hashlib, getpass
print(hashlib.sha256(getpass.getpass("Password: ").encode()).hexdigest())
PY
openssl rand -hex 32
```

## Run

```bash
.venv/bin/uvicorn vpn_monitor.web.app:app --host 127.0.0.1 --port 9100
```

See `examples/` for systemd and Nginx snippets.

## Privacy

Do not commit runtime data or credentials. This project is intended for self-operated nodes and authorized learning use.

## Tests

```bash
python -m compileall vpn_monitor tests
python -m unittest discover -s tests
```
