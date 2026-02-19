"""Plan-and-Execute agent loop.

Demonstrates the agentic workflow:
  1. Check health data (sleep, activity, HR)
  2. Calculate readiness score
  3. Load tasks from todo.json
  4. Propose an energy-aware rescheduled calendar
  5. Print a human-readable daily brief

Run: uv run python mcp_server/agent.py [YYYY-MM-DD]
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skills.summarizer import get_full_summary, calculate_readiness

TODO_PATH = Path(__file__).resolve().parent.parent / "data" / "todo.json"


def load_tasks() -> list[dict]:
    return json.loads(TODO_PATH.read_text()) if TODO_PATH.exists() else []


def plan_schedule(readiness: dict, tasks: list[dict]) -> dict:
    """Slot tasks into time blocks based on readiness score."""
    score = readiness.get("readiness_score")
    if score is None:
        return {"error": "Insufficient health data to plan."}

    fixed = [t for t in tasks if not t.get("flexible", True)]
    flex = [t for t in tasks if t.get("flexible", True)]
    high = [t for t in flex if t["energy_required"] == "high"]
    med = [t for t in flex if t["energy_required"] == "medium"]
    low = [t for t in flex if t["energy_required"] == "low"]

    blocks = {"morning": [], "midday": [], "afternoon": [], "evening": []}

    for t in fixed:
        pref = t.get("preferred_time", "")
        blocks["morning"].append(f"  [{pref}] {t['title']} ({t['duration_minutes']}min) — FIXED")

    if score >= 7:
        for t in high:
            blocks["morning"].append(f"  [08:00–10:00] {t['title']} ({t['duration_minutes']}min)")
        for t in med:
            blocks["midday"].append(f"  [10:30–12:00] {t['title']} ({t['duration_minutes']}min)")
        for t in low:
            blocks["afternoon"].append(f"  [14:00–16:00] {t['title']} ({t['duration_minutes']}min)")
    elif score >= 5:
        for t in low:
            blocks["morning"].append(f"  [09:00–10:00] {t['title']} ({t['duration_minutes']}min)")
        for t in med:
            blocks["midday"].append(f"  [10:30–12:00] {t['title']} ({t['duration_minutes']}min)")
        for t in high:
            blocks["afternoon"].append(f"  [14:00–16:00] {t['title']} ({t['duration_minutes']}min)")
    else:
        for t in low:
            blocks["morning"].append(f"  [09:00–10:00] {t['title']} ({t['duration_minutes']}min)")
        for t in med:
            blocks["midday"].append(f"  [10:30–12:00] {t['title']} ({t['duration_minutes']}min)")
        for t in high:
            blocks["evening"].append(f"  [16:00–18:00] {t['title']} ({t['duration_minutes']}min) ⚠ consider deferring")

    return blocks


def print_daily_brief(target_date: str):
    print(f"\n{'='*50}")
    print(f"  WELLNESS PLANNER — Daily Brief for {target_date}")
    print(f"{'='*50}\n")

    # Step 1: Health summary
    summary = get_full_summary(target_date)
    sleep = summary["sleep"]
    activity = summary["activity"]
    hr = summary["heart_rate"]

    if "error" not in sleep:
        print(f"SLEEP: {sleep['total_hours']}h (deep: {sleep['deep_sleep_hours']}h, "
              f"REM: {sleep['rem_sleep_hours']}h, woke {sleep['awakenings']}x)")
    else:
        print(f"SLEEP: {sleep['error']}")

    if "error" not in activity:
        workout_str = f", workout: {activity['workout']}" if activity["workout"] else ""
        print(f"ACTIVITY: {activity['steps']} steps, {activity['active_minutes']} active min, "
              f"{activity['calories_burned']} cal{workout_str}")
    else:
        print(f"ACTIVITY: {activity['error']}")

    if "error" not in hr:
        print(f"HEART RATE: resting {hr['resting_bpm']} bpm, "
              f"range {hr['min_bpm']}–{hr['max_bpm']} bpm, avg {hr['avg_bpm']} bpm")
    else:
        print(f"HEART RATE: {hr['error']}")

    # Step 2: Readiness
    readiness = calculate_readiness(target_date)
    score = readiness.get("readiness_score", "N/A")
    rec = readiness.get("recommendation", "")
    print(f"\nREADINESS: {score}/10 — {rec}")

    # Step 3: Load tasks
    tasks = load_tasks()
    print(f"\nTASKS LOADED: {len(tasks)} items")

    # Step 4: Propose schedule
    blocks = plan_schedule(readiness, tasks)
    if "error" in blocks:
        print(f"\n{blocks['error']}")
        return

    print(f"\nPROPOSED SCHEDULE:")
    for period, items in blocks.items():
        if items:
            print(f"\n  {period.upper()}:")
            for item in items:
                print(f"  {item}")

    print(f"\n{'='*50}\n")


def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = (date.today() - timedelta(days=1)).isoformat()

    print_daily_brief(target)


if __name__ == "__main__":
    main()
