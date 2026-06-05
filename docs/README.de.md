# VPN Monitor

[简体中文](../README.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | Deutsch | [Русский](README.ru.md)

VPN Monitor ist ein leichtes Dashboard zur Beobachtung von VPN-Traffic auf Domain-Ebene. Die erste Version unterstützt Xray access logs und speichert normalisierte Ereignisse in SQLite.

HTTPS-Verkehr wird nicht entschlüsselt. Erfasst werden nur Metadaten, die in Proxy-Logs bereits sichtbar sind.

## Funktionen

- FastAPI-App mit Jinja2-Templates und einfachem JavaScript/CSS.
- Anmeldung mit signierten HttpOnly-Cookies.
- Xray-access-log-Adapter und normalisiertes Ereignismodell.
- SQLite-Speicher.
- Übersicht, aktive Zugriffe, Top-Domains, aktuelle Ereignisse und CSV/JSON-Export.

## Installation

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp examples/vpn-monitor.env.example /etc/vpn-monitor.env
chmod 600 /etc/vpn-monitor.env
```

## Start

```bash
.venv/bin/uvicorn vpn_monitor.web.app:app --host 127.0.0.1 --port 9100
```

## Datenschutz

Dieses Projekt führt kein TLS-MITM durch, entschlüsselt keine HTTPS-Inhalte und extrahiert keine Zugangsdaten.
