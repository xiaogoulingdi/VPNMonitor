# VPN Monitor

[简体中文](../README.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Français](README.fr.md) | [Deutsch](README.de.md) | Русский

VPN Monitor — легкая панель мониторинга VPN-трафика на уровне доменов. Первая версия поддерживает Xray access log и сохраняет нормализованные события в SQLite.

Проект не расшифровывает HTTPS-трафик. Он записывает только метаданные, которые уже видны в логах прокси.

## Возможности

- FastAPI-приложение с Jinja2 и обычным JavaScript/CSS.
- Вход через подписанные HttpOnly cookies.
- Адаптер Xray access log и нормализованная модель событий.
- SQLite-хранилище.
- Сводка, активные подключения, топ доменов, последние события, экспорт CSV/JSON.

## Установка

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp examples/vpn-monitor.env.example /etc/vpn-monitor.env
chmod 600 /etc/vpn-monitor.env
```

## Запуск

```bash
.venv/bin/uvicorn vpn_monitor.web.app:app --host 127.0.0.1 --port 9100
```

## Конфиденциальность

Проект не выполняет TLS MITM, не расшифровывает HTTPS-содержимое и не извлекает учетные данные.
