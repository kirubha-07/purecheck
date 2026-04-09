import threading
from collections import deque
from typing import Dict


_LOCK = threading.Lock()
_API_RESPONSE_MS = deque(maxlen=500)
_PIPELINE_INGESTION_SEC = deque(maxlen=200)
_PIPELINE_SCORING_SEC = deque(maxlen=200)
_PIPELINE_TOTAL_SEC = deque(maxlen=200)


def _avg(values: deque) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def record_api_response(duration_seconds: float) -> None:
    with _LOCK:
        _API_RESPONSE_MS.append(duration_seconds * 1000.0)


def record_pipeline_metrics(ingestion_seconds: float, scoring_seconds: float, total_seconds: float) -> None:
    with _LOCK:
        _PIPELINE_INGESTION_SEC.append(float(ingestion_seconds))
        _PIPELINE_SCORING_SEC.append(float(scoring_seconds))
        _PIPELINE_TOTAL_SEC.append(float(total_seconds))


def get_system_metrics() -> Dict:
    with _LOCK:
        return {
            'avg_pipeline_latency': _avg(_PIPELINE_INGESTION_SEC),
            'avg_scoring_time': _avg(_PIPELINE_SCORING_SEC),
            'avg_api_response_time': _avg(_API_RESPONSE_MS),
            'last_pipeline_duration': round(_PIPELINE_TOTAL_SEC[-1], 4) if _PIPELINE_TOTAL_SEC else 0.0,
        }
