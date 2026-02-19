"""Token-optimized health data summarizer.

Instead of passing raw 24-hour heart rate data (48 readings) to the LLM,
this module computes compact statistical summaries that preserve the signal
while drastically reducing token usage.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "health.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def summarize_heart_rate(date: str) -> dict:
    """Return min/max/avg/resting heart rate for a date instead of raw readings."""
    conn = get_db()
    row = conn.execute(
        """
        SELECT
            MIN(bpm) AS min_bpm,
            MAX(bpm) AS max_bpm,
            ROUND(AVG(bpm), 1) AS avg_bpm,
            ROUND(AVG(CASE WHEN CAST(substr(timestamp, 12, 2) AS INTEGER) BETWEEN 0 AND 5 THEN bpm END), 1) AS resting_bpm,
            COUNT(*) AS sample_count
        FROM heart_rate_logs WHERE date = ?
        """,
        (date,),
    ).fetchone()
    conn.close()

    if not row or row["sample_count"] == 0:
        return {"error": f"No heart rate data for {date}"}

    return {
        "date": date,
        "min_bpm": row["min_bpm"],
        "max_bpm": row["max_bpm"],
        "avg_bpm": row["avg_bpm"],
        "resting_bpm": row["resting_bpm"],
        "sample_count": row["sample_count"],
    }


def summarize_sleep(date: str) -> dict:
    """Return a compact sleep summary for a date."""
    conn = get_db()
    row = conn.execute("SELECT * FROM sleep_logs WHERE date = ?", (date,)).fetchone()
    conn.close()

    if not row:
        return {"error": f"No sleep data for {date}"}

    return {
        "date": date,
        "bedtime": row["bedtime"],
        "wake_time": row["wake_time"],
        "total_hours": row["total_hours"],
        "deep_sleep_hours": row["deep_sleep_hours"],
        "rem_sleep_hours": row["rem_sleep_hours"],
        "awakenings": row["awakenings"],
        "sleep_quality": _rate_sleep(row["total_hours"], row["deep_sleep_hours"], row["awakenings"]),
    }


def summarize_activity(date: str) -> dict:
    """Return a compact activity summary for a date."""
    conn = get_db()
    row = conn.execute("SELECT * FROM activity_logs WHERE date = ?", (date,)).fetchone()
    conn.close()

    if not row:
        return {"error": f"No activity data for {date}"}

    return {
        "date": date,
        "steps": row["steps"],
        "active_minutes": row["active_minutes"],
        "calories_burned": row["calories_burned"],
        "workout": row["workouts"],
    }


def get_full_summary(date: str) -> dict:
    """Aggregate all health signals into a single token-efficient payload."""
    return {
        "sleep": summarize_sleep(date),
        "activity": summarize_activity(date),
        "heart_rate": summarize_heart_rate(date),
    }


def calculate_readiness(date: str) -> dict:
    """Compute a 1-10 readiness score from sleep, activity, and HR data.

    Weights: sleep quality 50%, resting HR 25%, prior-day exertion 25%.
    """
    sleep = summarize_sleep(date)
    hr = summarize_heart_rate(date)

    if "error" in sleep or "error" in hr:
        return {"date": date, "readiness_score": None, "reason": "Insufficient data"}

    sleep_score = _rate_sleep(sleep["total_hours"], sleep["deep_sleep_hours"], sleep["awakenings"])
    hr_score = _rate_resting_hr(hr["resting_bpm"])

    conn = get_db()
    prev_activity = conn.execute(
        "SELECT active_minutes FROM activity_logs WHERE date < ? ORDER BY date DESC LIMIT 1",
        (date,),
    ).fetchone()
    conn.close()

    exertion_score = 5.0
    if prev_activity:
        mins = prev_activity["active_minutes"]
        if mins < 30:
            exertion_score = 7.0
        elif mins < 60:
            exertion_score = 5.0
        else:
            exertion_score = 3.0

    readiness = round(sleep_score * 0.50 + hr_score * 0.25 + exertion_score * 0.25, 1)
    readiness = max(1.0, min(10.0, readiness))

    return {
        "date": date,
        "readiness_score": readiness,
        "components": {
            "sleep_score": sleep_score,
            "resting_hr_score": hr_score,
            "recovery_score": exertion_score,
        },
        "recommendation": _readiness_label(readiness),
    }


def _rate_sleep(total: float, deep: float, awakenings: int) -> float:
    score = 5.0
    if total >= 7.5:
        score += 2.0
    elif total >= 6.5:
        score += 1.0
    elif total < 5.5:
        score -= 2.0

    if deep >= 1.5:
        score += 1.5
    elif deep < 0.8:
        score -= 1.0

    if awakenings <= 1:
        score += 1.0
    elif awakenings >= 4:
        score -= 1.0

    return max(1.0, min(10.0, round(score, 1)))


def _rate_resting_hr(resting: float | None) -> float:
    if resting is None:
        return 5.0
    if resting < 55:
        return 9.0
    if resting < 60:
        return 7.5
    if resting < 65:
        return 6.0
    if resting < 72:
        return 4.5
    return 3.0


def _readiness_label(score: float) -> str:
    if score >= 8:
        return "Peak — ideal for demanding cognitive or physical tasks"
    if score >= 6:
        return "Good — handle normal workload, consider spacing intense tasks"
    if score >= 4:
        return "Moderate — stick to routine tasks, avoid overexertion"
    return "Low — prioritize rest and recovery, defer demanding work"
