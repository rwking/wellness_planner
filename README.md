# Wellness Planner

A local MCP agent that queries personal health data and provides energy-aware task scheduling.

## Data Note

**This project uses simulated data.** Health data is seeded from `data/seed_db.py` into a SQLite database. There is **no Apple Health integration** — real health data is not imported or synced.

## Running the Code

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) for dependency management

### Standalone Agent (no MCP server required)

Run the Plan-and-Execute agent loop locally:

```bash
uv run python mcp_server/agent.py [YYYY-MM-DD]
```

- Uses yesterday's date if no date is given.
- Reads from `data/health.db` and `data/todo.json`.
- Prints a daily brief: sleep, activity, heart rate, readiness score, and proposed schedule.

### MCP Server (for Cursor)

The MCP server is spawned by Cursor when needed — you do not start it manually in a separate terminal.

1. Configure Cursor to use the local MCP server (e.g. `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "wellness-planner": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/wellness_planner", "python", "mcp_server/server.py"]
    }
  }
}
```

2. Replace `/path/to/wellness_planner` with your actual project path.
3. Cursor will spawn the server and communicate over stdio.

### Other Commands

| Command | Purpose |
|---------|---------|
| `uv run python main.py` | Placeholder entry point |
| `uv run python data/seed_db.py` | Seed `data/health.db` with simulated data |

## MCP Tools

When the server is connected, these tools are available:

- `get_health_summary` — Aggregated sleep, activity, and heart rate for a date
- `calculate_readiness_score` — 1–10 readiness score for task timing
- `query_raw_logs` — Run read-only SQL against the health DB
- `get_tasks` — Load tasks from `todo.json`
- `propose_schedule` — Energy-aware schedule based on readiness and tasks
- `get_data_dictionary` — Schema introspection: column names, types, and sample values
- `run_analysis` — Execute a pandas/sqlite analysis script locally; returns stdout
- `generate_chart` — Produce a self-contained Observable Plot HTML chart
- `get_insights` — Retrieve previously saved findings from the Fact Store
- `save_insight` — Persist a discovered insight so it isn't re-computed next session

## Testing

There are two layers to test: the skills directly, and the MCP tools through Cursor chat.

### 1. Test skills directly (fast, no Cursor needed)

**Phase 1 — Sandbox execution:**

```bash
uv run python -c "
from skills.sandbox import run_python_analysis
r = run_python_analysis('''
df = pd.read_sql('SELECT date, total_hours FROM sleep_logs ORDER BY date DESC LIMIT 7', __import__('sqlite3').connect(DB_PATH))
print(df.to_string(index=False))
''')
print(r['output'])
"
```

**Phase 2 — Schema discovery:**

```bash
uv run python -c "
from skills.schema import get_data_dictionary
import json
print(json.dumps(get_data_dictionary(), indent=2))
"
```

**Phase 3 — Chart generation:**

```bash
uv run python -c "
import sqlite3
from skills.visualization import generate_chart
rows = sqlite3.connect('data/health.db').execute('SELECT date, total_hours FROM sleep_logs ORDER BY date').fetchall()
r = generate_chart([{'date': r[0], 'total_hours': r[1]} for r in rows], 'Sleep Trend', 'date', 'total_hours')
print(r)
"
```

Then open the `url` value in a browser to see the chart.

**Phase 4 — Fact Store:**

```bash
uv run python -c "
from skills.memory import save_insight, get_insights, clear_insights
save_insight('test_key', 'test value', 'manual test')
print(get_insights())
clear_insights()
"
```

### 2. Test end-to-end through Cursor (the real agentic loop)

Ask the agent questions in chat and watch the MCP tool calls fire in sequence:

- **Schema discovery:** *"What tables and columns are in the health database?"*
- **Analysis:** *"What's the correlation between my step count and sleep quality over the last 30 days?"*
  - Should trigger: `get_insights` → `get_data_dictionary` → `run_analysis` → `save_insight`
- **Chart:** *"Show me my resting heart rate trend as a chart."*
  - Should trigger: `run_analysis` → `generate_chart` → returns a file path
- **Memory:** *"What do you already know about my health patterns?"*
  - Should trigger: `get_insights` and return stored findings without re-running anything

### 3. Standalone agent CLI

```bash
uv run python mcp_server/agent.py 2026-02-18
```

Tests the non-MCP path (summarizer + readiness + scheduling) and confirms nothing broke during the Phase 1–4 additions.
