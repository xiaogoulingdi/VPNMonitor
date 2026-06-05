# VPN Monitor

[简体中文](../README.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | Español | [Français](README.fr.md) | [Deutsch](README.de.md) | [Русский](README.ru.md)

VPN Monitor es un panel ligero para observar tráfico de VPN a nivel de dominio. La primera versión admite logs de acceso de Xray y guarda eventos normalizados en SQLite.

No descifra tráfico HTTPS. Solo registra metadatos visibles en los logs del proxy.

## Funciones

- Aplicación FastAPI con Jinja2 y JavaScript/CSS nativo.
- Inicio de sesión con cookies HttpOnly firmadas.
- Adaptador para Xray access log y modelo de evento normalizado.
- Almacenamiento SQLite.
- Resumen, accesos activos, dominios principales, eventos recientes y exportación CSV/JSON.

## Instalación

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp examples/vpn-monitor.env.example /etc/vpn-monitor.env
chmod 600 /etc/vpn-monitor.env
```

## Ejecución

```bash
.venv/bin/uvicorn vpn_monitor.web.app:app --host 127.0.0.1 --port 9100
```

## Privacidad

El proyecto no realiza MITM TLS, no descifra contenido HTTPS y no extrae credenciales.
