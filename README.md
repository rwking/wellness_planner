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
