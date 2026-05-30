from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ServiceInfoSchema:
    name: str

    def as_dict(self) -> dict[str, str]:
        return {"name": self.name}


@dataclass(frozen=True, slots=True)
class ServiceProcessInfoSchema:
    pid: int | None = None
    status: str | None = None
    mem_usage_percent: float | None = None
    mem_usage: str | None = None
    vmem_usage: str | None = None
    proc_usage: str | None = None
    uptime_seconds: int | None = None
    uptime: str | None = None
    is_running: bool | None = None
    last_seen: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ServiceProcessInfoSchema:
        return cls(
            pid=data.get("pid"),
            status=data.get("status"),
            mem_usage_percent=data.get("mem_usage_percent"),
            mem_usage=data.get("mem_usage"),
            vmem_usage=data.get("vmem_usage"),
            proc_usage=data.get("proc_usage"),
            uptime_seconds=data.get("uptime_seconds"),
            uptime=data.get("uptime"),
            is_running=data.get("is_running"),
            last_seen=data.get("last_seen"),
        )

    def as_dict(self) -> dict[str, Any]:
        result = {
            "pid": self.pid,
            "status": self.status,
            "mem_usage_percent": self.mem_usage_percent,
            "mem_usage": self.mem_usage,
            "vmem_usage": self.vmem_usage,
            "proc_usage": self.proc_usage,
            "uptime_seconds": self.uptime_seconds,
            "uptime": self.uptime,
            "is_running": self.is_running,
            "last_seen": self.last_seen,
        }
        return {key: value for key, value in result.items() if value is not None}
