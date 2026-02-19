"""Seed a SQLite database with realistic sample health data for development."""

import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "health.db"


def create_tables(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sleep_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            bedtime TEXT NOT NULL,
            wake_time TEXT NOT NULL,
            total_hours REAL NOT NULL,
            deep_sleep_hours REAL NOT NULL,
            rem_sleep_hours REAL NOT NULL,
            awakenings INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            steps INTEGER NOT NULL,
            active_minutes INTEGER NOT NULL,
            calories_burned INTEGER NOT NULL,
            workouts TEXT
        );

        CREATE TABLE IF NOT EXISTS heart_rate_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            bpm INTEGER NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_hr_date ON heart_rate_logs(date);
    """)


def seed_data(conn: sqlite3.Connection, days: int = 30):
    today = datetime.now().date()

    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.isoformat()

        # Sleep data — realistic variation
        bedtime_hour = random.choice([22, 23, 23, 23, 0, 0, 1])
        bedtime_min = random.randint(0, 59)
        total_hours = round(random.uniform(5.0, 9.0), 1)
        deep = round(random.uniform(0.5, 2.0), 1)
        rem = round(random.uniform(1.0, 2.5), 1)

        bed_dt = datetime(date.year, date.month, date.day, bedtime_hour % 24, bedtime_min)
        wake_dt = bed_dt + timedelta(hours=total_hours)

        conn.execute(
            "INSERT OR IGNORE INTO sleep_logs (date, bedtime, wake_time, total_hours, deep_sleep_hours, rem_sleep_hours, awakenings) VALUES (?,?,?,?,?,?,?)",
            (date_str, bed_dt.strftime("%H:%M"), wake_dt.strftime("%H:%M"),
             total_hours, deep, rem, random.randint(0, 5)),
        )

        # Activity data
        is_workout_day = random.random() < 0.5
        workout_types = ["Running", "Weightlifting", "Yoga", "Cycling", "HIIT", "Swimming"]
        steps = random.randint(3000, 18000)
        active_min = random.randint(15, 90)
        calories = 1800 + int(steps * 0.04) + (300 if is_workout_day else 0)

        conn.execute(
            "INSERT OR IGNORE INTO activity_logs (date, steps, active_minutes, calories_burned, workouts) VALUES (?,?,?,?,?)",
            (date_str, steps, active_min, calories,
             random.choice(workout_types) if is_workout_day else None),
        )

        # Heart rate — one reading every 30 minutes for a 24-hour day
        for hour in range(24):
            for minute in (0, 30):
                ts = datetime(date.year, date.month, date.day, hour, minute)
                if 0 <= hour < 6:
                    bpm = random.randint(48, 62)
                elif 6 <= hour < 9:
                    bpm = random.randint(60, 85)
                elif 9 <= hour < 17:
                    bpm = random.randint(65, 110)
                elif 17 <= hour < 21:
                    bpm = random.randint(70, 140) if is_workout_day else random.randint(60, 95)
                else:
                    bpm = random.randint(55, 72)
                conn.execute(
                    "INSERT INTO heart_rate_logs (date, timestamp, bpm) VALUES (?,?,?)",
                    (date_str, ts.isoformat(), bpm),
                )

    conn.commit()


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    seed_data(conn)
    count = conn.execute("SELECT COUNT(*) FROM heart_rate_logs").fetchone()[0]
    print(f"Seeded {DB_PATH}: 30 days of sleep, activity, and {count} heart rate readings.")
    conn.close()


if __name__ == "__main__":
    main()
