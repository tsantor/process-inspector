from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger(__name__)


class ServiceCommandMetrics:
    """Thread-safe rolling debug metrics for service command execution."""

    _flush_interval_seconds = 1.0
    _lock = threading.Lock()
    _state: dict[tuple[str, str], dict[str, float | int]] = {}

    @classmethod
    def record(
        cls,
        *,
        backend: str,
        service_name: str,
        command: str,
        elapsed_ms: float,
        cache_state: str,
    ) -> None:
        now = time.monotonic()
        key = (backend, service_name)
        with cls._lock:
            bucket = cls._state.get(key)
            if bucket is None:
                bucket = {
                    "first_ts": now,
                    "total": 0,
                    "status_count": 0,
                    "pid_count": 0,
                    "cache_hit": 0,
                    "cache_miss": 0,
                    "cache_bypass": 0,
                    "elapsed_ms_total": 0.0,
                }
                cls._state[key] = bucket

            bucket["total"] += 1
            bucket["elapsed_ms_total"] += elapsed_ms
            if command == "status":
                bucket["status_count"] += 1
            elif command == "pid":
                bucket["pid_count"] += 1

            if cache_state == "hit":
                bucket["cache_hit"] += 1
            elif cache_state == "miss":
                bucket["cache_miss"] += 1
            else:
                bucket["cache_bypass"] += 1

            if now - float(bucket["first_ts"]) >= cls._flush_interval_seconds:
                cls._flush_locked(key, bucket)
                cls._state.pop(key, None)

    @classmethod
    def _flush_locked(
        cls, key: tuple[str, str], bucket: dict[str, float | int]
    ) -> None:
        backend, service_name = key
        total = int(bucket["total"])
        elapsed_ms_total = float(bucket["elapsed_ms_total"])
        avg_ms = elapsed_ms_total / total if total else 0.0
        logger.debug(
            (
                "%s aggregate service=%s window_s=%.2f total=%d status=%d pid=%d "
                "cache_hit=%d cache_miss=%d cache_bypass=%d elapsed_ms_total=%.2f "
                "elapsed_ms_avg=%.2f"
            ),
            backend,
            service_name,
            cls._flush_interval_seconds,
            total,
            int(bucket["status_count"]),
            int(bucket["pid_count"]),
            int(bucket["cache_hit"]),
            int(bucket["cache_miss"]),
            int(bucket["cache_bypass"]),
            elapsed_ms_total,
            avg_ms,
        )
