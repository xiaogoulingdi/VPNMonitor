# VPN Monitor

[简体中文](../README.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | Français | [Deutsch](README.de.md) | [Русский](README.ru.md)

VPN Monitor est un tableau de bord léger pour observer le trafic VPN au niveau des domaines. La première version prend en charge les logs d'accès Xray et stocke les événements normalisés dans SQLite.

Il ne déchiffre pas le trafic HTTPS. Il enregistre uniquement les métadonnées déjà visibles dans les logs du proxy.

## Fonctionnalités

- Application FastAPI avec templates Jinja2 et JavaScript/CSS natifs.
- Connexion applicative avec cookies HttpOnly signés.
- Adaptateur Xray access log et modèle d'événement normalisé.
- Stockage SQLite.
- Résumé, accès actifs, domaines principaux, événements récents, export CSV/JSON.

## Installation

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp examples/vpn-monitor.env.example /etc/vpn-monitor.env
chmod 600 /etc/vpn-monitor.env
```

## Exécution

```bash
.venv/bin/uvicorn vpn_monitor.web.app:app --host 127.0.0.1 --port 9100
```

## Confidentialité

Ce projet ne fait pas d'interception TLS, ne déchiffre pas le contenu HTTPS et n'extrait pas d'identifiants.
