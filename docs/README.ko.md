# VPN Monitor

[简体中文](../README.md) | [English](README.en.md) | [日本語](README.ja.md) | 한국어 | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md)

VPN Monitor는 개인 VPN 노드를 위한 가벼운 도메인 단위 트래픽 모니터링 패널입니다. 첫 버전은 Xray access log를 읽고 정규화된 이벤트를 SQLite에 저장합니다.

HTTPS 트래픽을 복호화하지 않습니다. 프록시 로그에 이미 보이는 메타데이터만 기록합니다.

## 기능

- FastAPI, Jinja2 템플릿, 순수 JavaScript/CSS 기반 UI.
- 서명된 HttpOnly Cookie를 사용하는 로그인.
- Xray access log 어댑터와 표준 이벤트 모델.
- SQLite 저장소.
- 요약 카드, 활성 접속, Top 도메인, 최근 이벤트, CSV/JSON 내보내기.

## 설치

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp examples/vpn-monitor.env.example /etc/vpn-monitor.env
chmod 600 /etc/vpn-monitor.env
```

## 실행

```bash
.venv/bin/uvicorn vpn_monitor.web.app:app --host 127.0.0.1 --port 9100
```

## 개인정보 보호

이 프로젝트는 TLS 중간자 처리, HTTPS 본문 복호화, 자격 증명 추출을 수행하지 않습니다.
