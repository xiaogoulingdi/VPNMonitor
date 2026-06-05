from datetime import datetime, timezone
import hashlib
import ipaddress
import re
import time

from vpn_monitor.adapters.base import BaseLogAdapter
from vpn_monitor.models import Event


ACCESS_RE = re.compile(
    r"^(?P<date>\d{4}/\d{2}/\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) "
    r"from (?P<source>\S+) (?P<action>accepted|rejected) "
    r"(?P<network>[a-zA-Z0-9]+):(?P<destination>.+?) "
    r"\[(?P<route>.+?)\](?: email: (?P<email>\S+))?$"
)

DOMESTIC_SUFFIXES = (
    ".cn", ".qq.com", ".tencent.com", ".weixin.com", ".wechat.com",
    ".alipay.com", ".taobao.com", ".tmall.com", ".jd.com",
    ".meituan.com", ".dianping.com", ".ele.me", ".amap.com",
    ".autonavi.com", ".baidu.com", ".bilibili.com", ".iqiyi.com",
    ".youku.com", ".cnki.net", ".cnki.cn", ".cnki.com.cn", ".cnki.com",
)

OVERSEAS_SUFFIXES = (
    ".google.com", ".youtube.com", ".googlevideo.com", ".github.com",
    ".openai.com", ".chatgpt.com", ".telegram.org", ".t.me",
    ".twitter.com", ".x.com", ".facebook.com", ".instagram.com",
    ".discord.com", ".reddit.com", ".netflix.com", ".spotify.com",
)


def safe_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def split_host_port(value: str) -> tuple[str, int | None]:
    value = value.strip()
    if value.startswith("[") and "]:" in value:
        host, port = value.rsplit("]:", 1)
        return host[1:], safe_int(port)
    if ":" in value:
        host, port = value.rsplit(":", 1)
        if port.isdigit():
            return host, int(port)
    return value, None


def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_private_ip(value: str) -> bool:
    try:
        addr = ipaddress.ip_address(value)
    except ValueError:
        return False
    return addr.is_private or addr.is_loopback or addr.is_link_local


def parse_route(route: str) -> tuple[str, str]:
    if ">>" in route:
        left, right = route.split(">>", 1)
    elif "->" in route:
        left, right = route.split("->", 1)
    else:
        left, right = route, ""
    return left.strip(), right.strip()


def classify(destination: str, inbound: str, source_ip: str) -> str:
    host = (destination or "").lower()
    if inbound == "API_INBOUND" or host in ("127.0.0.1", "localhost") or is_private_ip(source_ip or ""):
        return "internal"
    if host.endswith(DOMESTIC_SUFFIXES) or host == "cn":
        return "domestic"
    if host.endswith(OVERSEAS_SUFFIXES):
        return "overseas"
    if is_ip(host):
        return "ip"
    return "other"


class XrayAccessLogAdapter(BaseLogAdapter):
    name = "xray_access_log"

    def parse_line(self, raw: str) -> Event | None:
        line = raw.strip()
        match = ACCESS_RE.match(line)
        if not match:
            return None
        raw_dt = f"{match.group('date')} {match.group('time')}"
        try:
            dt = datetime.strptime(raw_dt, "%Y/%m/%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
        source_ip, source_port = split_host_port(match.group("source"))
        destination, dest_port = split_host_port(match.group("destination"))
        inbound, outbound = parse_route(match.group("route"))
        normalized_destination = destination.lower()
        domain = "" if is_ip(destination) else normalized_destination
        category = classify(destination, inbound, source_ip)
        raw_hash = hashlib.sha256(line.encode("utf-8", "replace")).hexdigest()
        return Event(
            ts=int(dt.timestamp()), time_utc=dt.isoformat(), source_ip=source_ip,
            source_port=source_port, action=match.group("action"),
            network=match.group("network").lower(), destination=normalized_destination,
            domain=domain, dest_port=dest_port, inbound=inbound, outbound=outbound,
            email=match.group("email") or "", category=category,
            is_internal=1 if category == "internal" else 0, raw=line,
            raw_hash=raw_hash, created_at=int(time.time()),
        )
