"""Schema discovery for the health database.

Returns a structured data dictionary — column names, types, row counts, and
sample values — so an LLM agent can build an accurate mental model of the
data before writing SQL or analysis scripts.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "health.db"

_SAMPLE_ROWS = 3


def get_data_dictionary() -> dict:
    """Introspect the health database and return a structured schema summary.

    For each table, returns:
      - row_count: total rows in the table.
      - columns: list of dicts with name, type, nullable.
      - samples: up to 3 representative rows as a list of dicts.

    Returns:
        dict keyed by table name, each containing row_count, columns, samples.
        On error, returns {"error": "<message>"}.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]

        result: dict[str, dict] = {}

        for table in tables:
            row_count: int = conn.execute(
                f"SELECT COUNT(*) FROM {table}"  # noqa: S608 — internal schema only
            ).fetchone()[0]

            pragma_rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
            columns = [
                {
                    "name": row["name"],
                    "type": row["type"] or "TEXT",
                    "nullable": not row["notnull"],
                }
                for row in pragma_rows
                if row["name"] != "id"
            ]

            sample_rows = conn.execute(
                f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT {_SAMPLE_ROWS}"  # noqa: S608
            ).fetchall()
            samples = [
                {k: v for k, v in dict(row).items() if k != "id"}
                for row in sample_rows
            ]

            result[table] = {
                "row_count": row_count,
                "columns": columns,
                "samples": samples,
            }

        return result

    except Exception as exc:
        return {"error": str(exc)}
    finally:
        conn.close()
