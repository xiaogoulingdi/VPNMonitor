from dataclasses import asdict, dataclass
from sqlite3 import Row


@dataclass(frozen=True)
class Event:
    ts: int
    time_utc: str
    source_ip: str
    source_port: int | None
    action: str
    network: str
    destination: str
    domain: str
    dest_port: int | None
    inbound: str
    outbound: str
    email: str
    category: str
    is_internal: int
    raw: str
    raw_hash: str
    created_at: int

    def as_db_dict(self) -> dict:
        return asdict(self)


def row_to_dict(row: Row) -> dict:
    return {key: row[key] for key in row.keys()}
