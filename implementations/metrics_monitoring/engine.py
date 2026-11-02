"""
Metrics Monitoring & Alerting System (Prometheus-style Time Series Engine)
Chapter 20: Metrics Monitoring and Alerting System

Architecture:
1. Time-Series Data Model: metric_name + labels (key-value tags) + timestamp + float value.
2. Sliding / Tumbling Aggregations: Computes SUM, AVG, MIN, MAX, P99 over time windows.
3. Alerting Engine: Evaluates dynamic threshold rules and manages alert states (OK, PENDING, FIRING).
"""

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import threading
import time
from typing import Callable, Dict, List, Optional, Tuple


class AlertState(str, Enum):
    OK = "OK"
    PENDING = "PENDING"
    FIRING = "FIRING"


@dataclass
class MetricPoint:
    metric_name: str
    labels: Dict[str, str]
    timestamp: float
    value: float


@dataclass
class AlertRule:
    rule_name: str
    metric_name: str
    threshold: float
    operator: str  # ">", "<", ">=", "<="
    duration_samples: int = 2
    state: AlertState = AlertState.OK
    pending_count: int = 0


class MetricsMonitoringEngine:
    """
    In-memory Time Series and Alerting Engine.
    """

    def __init__(self, retention_seconds: float = 3600.0):
        self.retention = retention_seconds
        # series_key -> deque of MetricPoint
        self._series: Dict[str, deque] = {}
        self._alert_rules: List[AlertRule] = []
        self._alert_history: List[Dict] = []
        self._lock = threading.Lock()

    def _make_series_key(self, metric_name: str, labels: Dict[str, str]) -> str:
        sorted_labels = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{metric_name}{{{sorted_labels}}}"

    def record_metric(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        labels = labels or {}
        key = self._make_series_key(metric_name, labels)
        now = time.time()
        point = MetricPoint(metric_name=metric_name, labels=labels, timestamp=now, value=value)

        with self._lock:
            if key not in self._series:
                self._series[key] = deque()
            q = self._series[key]
            q.append(point)

            # Evict aged points beyond retention window
            cutoff = now - self.retention
            while q and q[0].timestamp < cutoff:
                q.popleft()

        # Trigger alert evaluation
        self._evaluate_alerts(metric_name, value)

    def register_alert_rule(self, rule: AlertRule) -> None:
        with self._lock:
            self._alert_rules.append(rule)

    def _evaluate_alerts(self, metric_name: str, latest_value: float) -> None:
        with self._lock:
            for rule in self._alert_rules:
                if rule.metric_name != metric_name:
                    continue

                breached = False
                if rule.operator == ">" and latest_value > rule.threshold:
                    breached = True
                elif rule.operator == "<" and latest_value < rule.threshold:
                    breached = True
                elif rule.operator == ">=" and latest_value >= rule.threshold:
                    breached = True
                elif rule.operator == "<=" and latest_value <= rule.threshold:
                    breached = True

                if breached:
                    rule.pending_count += 1
                    if rule.pending_count >= rule.duration_samples:
                        rule.state = AlertState.FIRING
                        self._alert_history.append({
                            "rule": rule.rule_name,
                            "metric": metric_name,
                            "value": latest_value,
                            "state": "FIRING",
                            "timestamp": time.time(),
                        })
                    else:
                        rule.state = AlertState.PENDING
                else:
                    if rule.state != AlertState.OK:
                        self._alert_history.append({
                            "rule": rule.rule_name,
                            "metric": metric_name,
                            "state": "RESOLVED",
                            "timestamp": time.time(),
                        })
                    rule.state = AlertState.OK
                    rule.pending_count = 0

    def query_aggregate(self, metric_name: str, window_seconds: float = 60.0) -> Dict[str, float]:
        """Calculates SUM, AVG, MIN, MAX over recent time window."""
        with self._lock:
            now = time.time()
            cutoff = now - window_seconds
            all_points: List[float] = []

            for key, q in self._series.items():
                if key.startswith(metric_name):
                    for pt in q:
                        if pt.timestamp >= cutoff:
                            all_points.append(pt.value)

        if not all_points:
            return {"count": 0, "avg": 0.0, "min": 0.0, "max": 0.0, "sum": 0.0}

        return {
            "count": len(all_points),
            "sum": round(sum(all_points), 3),
            "avg": round(sum(all_points) / len(all_points), 3),
            "min": round(min(all_points), 3),
            "max": round(max(all_points), 3),
        }

    def get_firing_alerts(self) -> List[AlertRule]:
        with self._lock:
            return [r for r in self._alert_rules if r.state == AlertState.FIRING]

