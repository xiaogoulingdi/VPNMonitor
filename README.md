# VPN Monitor

轻量级 VPN 域名级流量监控面板。第一版面向个人自建节点，支持读取 Xray access log，并把标准化后的访问记录保存到 SQLite。

> 隐私边界：本项目不解密 HTTPS，不做 TLS 中间人，不读取网页正文、账号密码或表单内容。它只记录代理服务端日志里已经可见的元数据，例如时间、来源 IP、目标域名/IP、入站节点、用户/设备、协议和分类。

## 多语言文档

- [English](docs/README.en.md)
- [日本語](docs/README.ja.md)
- [한국어](docs/README.ko.md)
- [Español](docs/README.es.md)
- [Français](docs/README.fr.md)
- [Deutsch](docs/README.de.md)
- [Русский](docs/README.ru.md)

## 功能

- FastAPI Web 应用，Jinja2 模板页，原生 JavaScript/CSS 前端。
- 应用内登录，使用签名 HttpOnly Cookie。
- Xray access log 适配器，把日志解析为统一事件模型。
- SQLite 存储，使用 Python 标准库，不引入复杂数据库依赖。
- 总览卡片、当前活跃访问、Top 域名、用户/设备统计、小时趋势、最近访问记录。
- 支持 CSV / JSON 导出，方便后续分析。
- 适配器式结构，后续可以扩展 Marzban API、Sing-box、Mihomo 等数据源。

## 目录结构

```text
vpn_monitor/
  adapters/          # 数据源解析器。第一版包含 Xray access log。
  services/          # 采集器和统计查询逻辑。
  web/               # FastAPI 应用、路由、模板、静态资源。
  auth.py            # 密码校验和签名会话 Cookie。
  config.py          # 环境变量配置。
  db.py              # SQLite schema 和写入逻辑。
  models.py          # 标准化事件模型。
examples/            # env、systemd、Nginx 示例。
scripts/             # 本地开发脚本。
tests/               # 单元测试。
```

项目部署入口是：

```text
vpn_monitor.web.app:app
```

## 安装

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

准备安全的环境变量文件：

```bash
cp examples/vpn-monitor.env.example /etc/vpn-monitor.env
chmod 600 /etc/vpn-monitor.env
```

生成登录密码哈希和会话密钥：

```bash
python3 - <<'PY'
import hashlib, getpass
print(hashlib.sha256(getpass.getpass("Password: ").encode()).hexdigest())
PY
openssl rand -hex 32
```

把生成结果写入 `/etc/vpn-monitor.env`。

## 运行

开发模式：

```bash
MONITOR_COOKIE_PATH=/ MONITOR_COLLECTOR_ENABLED=false scripts/run_dev.sh
```

生产运行示例：

```bash
.venv/bin/uvicorn vpn_monitor.web.app:app --host 127.0.0.1 --port 9100
```

systemd 和 Nginx 示例见：

- `examples/vpn-monitor.service.example`
- `examples/nginx-monitor.example.conf`

## 配置

常用环境变量：

- `MONITOR_USERNAME`：登录用户名。
- `MONITOR_PASSWORD_SHA256`：登录密码的 SHA-256 哈希。
- `MONITOR_SESSION_SECRET`：签名会话 Cookie 的随机密钥。
- `MONITOR_DB`：SQLite 数据库路径。
- `XRAY_ACCESS_LOG`：Xray access log 路径。
- `MONITOR_HOST` / `MONITOR_PORT`：监听地址和端口。
- `MONITOR_RETENTION_DAYS`：结构化记录保留天数。
- `MONITOR_COOKIE_PATH`：通过 Nginx `/monitor/` 反代时建议设为 `/monitor`。
- `MONITOR_COLLECTOR_ENABLED`：开发只读模式可设为 `false`。

## API

- `GET /login`
- `POST /login`
- `GET /logout`
- `GET /health`
- `GET /api/options`
- `GET /api/summary`
- `GET /api/active`
- `GET /api/events`
- `GET /api/export.csv`
- `GET /api/export.json`

除 `/health` 外，API 需要有效登录会话。

## 安全与隐私

- 不要把真实数据库、日志、`.env`、`MONITOR_LOGIN.txt` 上传到 GitHub。
- `.gitignore` 已排除 SQLite 数据库、WAL 文件、本地环境变量、登录备忘和 Python 缓存。
- 建议通过 Nginx 反代并配置 HTTPS 后再公网使用。
- 本项目适合个人学习、自建节点观测和自有设备分析，不应用于未授权监控他人流量。

## 测试

```bash
python -m compileall vpn_monitor tests
python -m unittest discover -s tests
```
