# VPN Monitor

[简体中文](../README.md) | [English](README.en.md) | 日本語 | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md)

VPN Monitor は、個人の VPN ノード向けの軽量なドメイン単位トラフィック監視パネルです。最初のバージョンは Xray access log を読み取り、正規化したイベントを SQLite に保存します。

HTTPS 通信の復号は行いません。記録するのは、プロキシログにすでに表示されるメタデータだけです。

## 主な機能

- FastAPI、Jinja2 テンプレート、Vanilla JavaScript/CSS による軽量 UI。
- 署名付き HttpOnly Cookie を使ったログイン。
- Xray access log アダプターと標準化イベントモデル。
- SQLite ストレージ。
- サマリー、現在のアクティブアクセス、Top ドメイン、最近のイベント、CSV/JSON エクスポート。

## インストール

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp examples/vpn-monitor.env.example /etc/vpn-monitor.env
chmod 600 /etc/vpn-monitor.env
```

## 実行

```bash
.venv/bin/uvicorn vpn_monitor.web.app:app --host 127.0.0.1 --port 9100
```

## プライバシー

このプロジェクトは TLS の中間者処理、HTTPS 本文の復号、資格情報の抽出を行いません。自分で運用するノードと、許可された学習用途向けです。
