"""JSON-based Fact Store for persisting agent-discovered insights.

The agent calls save_insight after completing an analysis to record a key
finding. On subsequent questions, it calls get_insights first — if a
relevant fact already exists, it skips re-running the analysis.

Insights are stored in data/insights.json as a list of records.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

INSIGHTS_PATH = Path(__file__).resolve().parent.parent / "data" / "insights.json"


def _load() -> list[dict]:
    if not INSIGHTS_PATH.exists():
        return []
    try:
        return json.loads(INSIGHTS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(insights: list[dict]) -> None:
    INSIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    INSIGHTS_PATH.write_text(
        json.dumps(insights, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_insight(key: str, value: str, source: str) -> dict:
    """Persist a discovered insight to the Fact Store.

    If an insight with the same key already exists, it is overwritten.
    This keeps the store compact — one canonical fact per key.

    Args:
        key: Short, snake_case identifier (e.g. "peak_energy_time",
            "worst_sleep_trigger", "avg_readiness_last_30d").
        value: Human-readable finding (e.g. "10 AM", "late evening workouts",
            "6.4 / 10").
        source: Description of what analysis produced this insight
            (e.g. "30-day correlation: steps vs. sleep quality").

    Returns:
        dict with keys: key, value, source, saved_at, action ("created"|"updated").
    """
    insights = _load()
    now = datetime.now(timezone.utc).isoformat()

    existing = next((i for i in insights if i["key"] == key), None)
    action = "updated" if existing else "created"

    record = {"key": key, "value": value, "source": source, "saved_at": now}

    if existing:
        existing.update(record)
    else:
        insights.append(record)

    _save(insights)
    return {**record, "action": action}


def get_insights(key: str | None = None) -> list[dict]:
    """Retrieve insights from the Fact Store.

    Args:
        key: Optional key to filter by. If omitted, returns all insights.

    Returns:
        List of insight dicts (key, value, source, saved_at), newest first.
        Returns an empty list if no insights are stored.
    """
    insights = sorted(_load(), key=lambda r: r.get("saved_at", ""), reverse=True)
    if key:
        insights = [i for i in insights if i["key"] == key]
    return insights


def clear_insights() -> dict:
    """Delete all stored insights from the Fact Store.

    Returns:
        dict with key: cleared (int) — number of records removed.
    """
    count = len(_load())
    _save([])
    return {"cleared": count}
