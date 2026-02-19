"""Wellness Planner MCP Server.

Exposes health data tools via the Model Context Protocol so an LLM agent
can query sleep, activity, and heart-rate data, compute readiness scores,
and build energy-aware schedules.
"""

import json
import sqlite3
from datetime import date
from pathlib import Path

from mcp.server.fastmcp import FastMCP

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skills.summarizer import (
    get_full_summary,
    calculate_readiness,
    summarize_heart_rate,
    summarize_sleep,
    summarize_activity,
)
from skills.sandbox import run_python_analysis as _run_python_analysis
from skills.schema import get_data_dictionary as _get_data_dictionary
from skills.visualization import generate_chart as _generate_chart
from skills.memory import save_insight as _save_insight, get_insights as _get_insights

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "health.db"
TODO_PATH = Path(__file__).resolve().parent.parent / "data" / "todo.json"

mcp = FastMCP(
    "Wellness Planner",
    instructions="Personal health data agent — sleep, activity, heart rate, and readiness scoring",
)


@mcp.tool()
def get_health_summary(target_date: str | None = None) -> dict:
    """Get an aggregated health summary (sleep, activity, heart rate) for a date.

    Args:
        target_date: ISO date string (YYYY-MM-DD). Defaults to today.
    """
    target_date = target_date or date.today().isoformat()
    return get_full_summary(target_date)


@mcp.tool()
def calculate_readiness_score(target_date: str | None = None) -> dict:
    """Calculate a 1-10 readiness score based on sleep quality, resting heart rate,
    and prior-day exertion. Use this to decide when to schedule demanding tasks.

    Args:
        target_date: ISO date string (YYYY-MM-DD). Defaults to today.
    """
    target_date = target_date or date.today().isoformat()
    return calculate_readiness(target_date)


@mcp.tool()
def query_raw_logs(query: str) -> list[dict]:
    """Run a read-only SQL query against the health database.

    Available tables:
    - sleep_logs (date, bedtime, wake_time, total_hours, deep_sleep_hours, rem_sleep_hours, awakenings)
    - activity_logs (date, steps, active_minutes, calories_burned, workouts)
    - heart_rate_logs (date, timestamp, bpm)

    Args:
        query: A SELECT SQL query. Only read operations are allowed.
    """
    normalized = query.strip().upper()
    if not normalized.startswith("SELECT"):
        return [{"error": "Only SELECT queries are permitted."}]

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows[:100]]
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        conn.close()


@mcp.tool()
def get_tasks() -> list[dict]:
    """Return the current task list from todo.json. Each task has an energy_required
    level (high/medium/low) and preferred_time slot."""
    if not TODO_PATH.exists():
        return [{"error": "todo.json not found"}]
    return json.loads(TODO_PATH.read_text())


@mcp.tool()
def propose_schedule(target_date: str | None = None) -> dict:
    """Propose an energy-aware daily schedule based on today's readiness score
    and the task list. High-energy tasks are placed when readiness supports them.

    Args:
        target_date: ISO date string (YYYY-MM-DD). Defaults to today.
    """
    target_date = target_date or date.today().isoformat()
    readiness = calculate_readiness(target_date)
    tasks = json.loads(TODO_PATH.read_text()) if TODO_PATH.exists() else []

    score = readiness.get("readiness_score")
    if score is None:
        return {"error": "Cannot schedule — insufficient health data", "readiness": readiness}

    morning, midday, afternoon, evening = [], [], [], []

    fixed = [t for t in tasks if not t.get("flexible", True)]
    flex = [t for t in tasks if t.get("flexible", True)]

    for t in fixed:
        pref = t.get("preferred_time", "")
        if ":" in pref:
            morning.append({**t, "scheduled_time": pref})
        else:
            afternoon.append({**t, "scheduled_time": "TBD"})

    high = [t for t in flex if t["energy_required"] == "high"]
    med = [t for t in flex if t["energy_required"] == "medium"]
    low = [t for t in flex if t["energy_required"] == "low"]

    if score >= 7:
        morning.extend([{**t, "scheduled_time": "08:00-10:00"} for t in high])
        midday.extend([{**t, "scheduled_time": "10:30-12:00"} for t in med])
        afternoon.extend([{**t, "scheduled_time": "14:00-16:00"} for t in low])
        evening.extend([])
    elif score >= 5:
        afternoon.extend([{**t, "scheduled_time": "14:00-16:00"} for t in high])
        morning.extend([{**t, "scheduled_time": "09:00-10:30"} for t in med])
        midday.extend([{**t, "scheduled_time": "10:30-12:00"} for t in low])
    else:
        evening.extend([{**t, "scheduled_time": "16:00-18:00", "note": "Consider deferring"} for t in high])
        morning.extend([{**t, "scheduled_time": "09:00-10:30"} for t in low])
        midday.extend([{**t, "scheduled_time": "10:30-12:00"} for t in med])

    return {
        "date": target_date,
        "readiness": readiness,
        "schedule": {
            "morning": morning,
            "midday": midday,
            "afternoon": afternoon,
            "evening": evening,
        },
    }


@mcp.tool()
def get_data_dictionary() -> dict:
    """Return a structured schema summary of the health database.

    Call this before writing any SQL query or run_analysis script to verify
    column names, data types, and representative sample values. This prevents
    hallucinated column names and bad JOINs.

    Returns a dict keyed by table name, each containing:
      - row_count: total rows.
      - columns: list of {name, type, nullable}.
      - samples: up to 3 representative rows.
    """
    return _get_data_dictionary()


@mcp.tool()
def run_analysis(script: str) -> dict:
    """Execute a Python analysis script against the health database.

    The script runs in an isolated subprocess. DB_PATH, sqlite3, and pandas
    are pre-injected — no imports needed. Results must be printed to stdout.
    Scripts timeout after 30 seconds; output is capped at 4000 characters.

    Available tables:
    - sleep_logs (date, bedtime, wake_time, total_hours, deep_sleep_hours, rem_sleep_hours, awakenings)
    - activity_logs (date, steps, active_minutes, calories_burned, workouts)
    - heart_rate_logs (date, timestamp, bpm)

    Example script:
        df = pd.read_sql("SELECT date, total_hours FROM sleep_logs ORDER BY date", sqlite3.connect(DB_PATH))
        print(df.describe().to_string())

    Args:
        script: Python source code to execute. Print all results to stdout.

    Returns:
        dict with keys: output (str), error (str|None), exit_code (int), truncated (bool).
    """
    return _run_python_analysis(script)


@mcp.tool()
def generate_chart(
    data: list[dict],
    title: str,
    x: str,
    y: str,
    mark_type: str = "line",
    filename: str | None = None,
) -> dict:
    """Generate a self-contained Observable Plot HTML chart from tabular data.

    Saves the chart to data/charts/ and returns the file path. Open the path
    in a browser to view the interactive chart. Raw data is embedded in the
    HTML — it does not re-enter the chat context.

    Args:
        data: List of dicts representing the data points (e.g. from run_analysis).
        title: Chart title displayed as a heading.
        x: Column name for the x-axis.
        y: Column name for the y-axis.
        mark_type: One of "line", "dot", "bar", "area", "boxX". Defaults to "line".
        filename: Optional output filename. Auto-generated from title + timestamp if omitted.

    Returns:
        dict with keys: path (str), url (str), rows (int).
    """
    return _generate_chart(data=data, title=title, x=x, y=y, mark_type=mark_type, filename=filename)


@mcp.tool()
def get_insights(key: str | None = None) -> list[dict]:
    """Retrieve previously saved insights from the Fact Store.

    Call this at the START of any analysis session. If a relevant insight
    already exists, return it directly — do not re-run the analysis.

    Args:
        key: Optional snake_case key to filter (e.g. "peak_energy_time").
            If omitted, returns all stored insights newest-first.

    Returns:
        List of dicts with keys: key, value, source, saved_at.
        Empty list if no insights are stored.
    """
    return _get_insights(key)


@mcp.tool()
def save_insight(key: str, value: str, source: str) -> dict:
    """Persist a discovered insight to the Fact Store.

    Call this AFTER completing an analysis to record the key finding.
    Existing insights with the same key are overwritten — one canonical
    fact per key keeps the store compact.

    Args:
        key: Short snake_case identifier (e.g. "peak_energy_time",
            "worst_sleep_trigger", "avg_readiness_last_30d").
        value: Human-readable finding (e.g. "10 AM", "late workouts", "6.4/10").
        source: What analysis produced this (e.g. "30-day HR correlation").

    Returns:
        dict with keys: key, value, source, saved_at, action ("created"|"updated").
    """
    return _save_insight(key=key, value=value, source=source)


if __name__ == "__main__":
    mcp.run(transport="stdio")
