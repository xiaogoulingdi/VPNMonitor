# VPS 运维说明

本文记录 VPN Monitor、Marzban 的常用路径、服务命令，以及如何手动维护 Clash 分流规则。

> 不要把真实登录密码、订阅链接、数据库或访问日志提交到 GitHub。本文档只保留通用运维方法。

## VPN Monitor

默认安装目录：

```bash
/opt/vpn-monitor
```

环境变量文件：

```bash
/etc/vpn-monitor.env
```

登录备忘文件：

```bash
/root/vpn-monitor-login.txt
```

SQLite 数据库：

```bash
/var/lib/vpn-monitor/monitor.db
```

默认读取的 Xray access log：

```bash
/var/lib/marzban/xray_access.log
```

常用命令：

```bash
systemctl status vpn-monitor.service
systemctl restart vpn-monitor.service
systemctl stop vpn-monitor.service
systemctl start vpn-monitor.service
journalctl -u vpn-monitor.service --no-pager -n 80
```

默认服务只监听本机：

```text
127.0.0.1:9100
```

公网访问建议通过 Nginx 反代和 HTTPS。

## Marzban

常见目录：

```bash
/opt/marzban
/var/lib/marzban
```

常见配置文件：

```bash
/opt/marzban/.env
/opt/marzban/docker-compose.yml
/var/lib/marzban/xray_config.json
```

常见数据库路径：

```bash
/var/lib/marzban/db.sqlite3
```

常用命令：

```bash
docker ps
docker logs --tail 100 marzban-marzban-1
docker exec -it marzban-marzban-1 python /code/marzban-cli.py admin list
docker exec -it marzban-marzban-1 python /code/marzban-cli.py user list
```

重置 Marzban 管理员密码：

```bash
docker exec -it marzban-marzban-1 python /code/marzban-cli.py admin update -u <admin-username>
```

## 手动维护 Clash 分流规则

如果 Marzban 使用自定义 Clash 模板，通常会在 `.env` 中看到类似配置：

```text
CUSTOM_TEMPLATES_DIRECTORY="/var/lib/marzban/templates/"
CLASH_SUBSCRIPTION_TEMPLATE="clash/default.yml"
```

对应模板路径通常是：

```bash
/var/lib/marzban/templates/clash/default.yml
```

建议优先修改模板文件，而不是逐个修改客户端。客户端更新订阅后会拿到新规则。

### 推荐规则结构

```yaml
proxy-groups:
  - name: Proxy
    type: select
    proxies:
      - Automatic
      - 节点名称

  - name: Domestic
    type: select
    proxies:
      - DIRECT
      - Proxy

  - name: Final
    type: select
    proxies:
      - Proxy
      - DIRECT

rules:
  - DOMAIN-SUFFIX,example.cn,Domestic
  - DOMAIN-SUFFIX,qq.com,Domestic
  - DOMAIN-SUFFIX,wechat.com,Domestic
  - GEOIP,CN,Domestic
  - MATCH,Final
```

日常建议：

- 国内网站和国内 IP：放到 `Domestic`，默认 `DIRECT`。
- 国外网站：放到 `Proxy`。
- 不确定的流量：最后交给 `MATCH,Final`。
- 不建议一次性导入太多来路不明的规则，先从确实经常访问的网站开始加。

### 常用规则类型

```yaml
- DOMAIN-SUFFIX,example.com,Proxy
- DOMAIN-SUFFIX,example.cn,Domestic
- DOMAIN,www.example.com,Proxy
- DOMAIN-KEYWORD,google,Proxy
- GEOIP,CN,Domestic
- MATCH,Final
```

### 修改后如何生效

1. 备份模板：

```bash
cp /var/lib/marzban/templates/clash/default.yml /var/lib/marzban/templates/clash/default.yml.bak.$(date +%Y%m%d-%H%M%S)
```

2. 编辑模板：

```bash
nano /var/lib/marzban/templates/clash/default.yml
```

3. 保存后先在客户端更新订阅测试。

4. 如果订阅没有变化，再重启 Marzban 容器：

```bash
docker restart marzban-marzban-1
```

5. 在 Clash Verge / Clash Mate / Shadowrocket 中手动更新订阅。

### 注意事项

- YAML 缩进很重要，尽量用空格，不要用 Tab。
- `rules:` 里的规则顺序从上到下匹配，越具体的规则越靠前。
- `MATCH` 必须放最后。
- 如果规则写错，Clash 客户端可能无法导入订阅。
- 改规则前一定先备份模板。

## Marzban 用户显示

VPN Monitor 的流量记录来自 Xray access log。没有产生新流量的用户原本不会出现在统计里。

当前版本可以额外只读 Marzban SQLite 数据库，把 Marzban 中存在的用户合并到用户筛选和用户统计中。默认路径：

```bash
/var/lib/marzban/db.sqlite3
```

如果数据库路径不同，可以在 `/etc/vpn-monitor.env` 中设置：

```bash
MARZBAN_DB=/path/to/db.sqlite3
```
