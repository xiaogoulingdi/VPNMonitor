from abc import ABC, abstractmethod

from vpn_monitor.models import Event


class BaseLogAdapter(ABC):
    name = "base"

    @abstractmethod
    def parse_line(self, raw: str) -> Event | None:
        """Parse one raw log line into a normalized event."""
