"""Basic metrics instrumentation."""

import time
from collections import defaultdict
from threading import Lock

_lock = Lock()
_counters: dict[str, int] = defaultdict(int)
_histograms: dict[str, list[float]] = defaultdict(list)


def inc(name: str, amount: int = 1) -> None:
    with _lock:
        _counters[name] += amount


def observe(name: str, value: float) -> None:
    with _lock:
        _histograms[name].append(value)


def get_metrics() -> dict:
    with _lock:
        result = {
            "counters": dict(_counters),
            "histograms": {},
        }
        for name, values in _histograms.items():
            if values:
                result["histograms"][name] = {
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                }
        return result


class Timer:
    """Context manager to measure elapsed time."""

    def __init__(self, metric_name: str):
        self.metric_name = metric_name
        self.start = 0.0

    def __enter__(self):
        self.start = time.monotonic()
        return self

    def __exit__(self, *args):
        elapsed = time.monotonic() - self.start
        observe(self.metric_name, elapsed)
