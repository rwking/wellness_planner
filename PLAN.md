# The Wellness Planner: Health Data Agent

Goal: Build a local agent that uses MCP (Model Context Protocol) to query personal health data and provides energy-aware task scheduling.

## Phase 1: Environment Setup
- [ ] Initialize Python environment using `uv`.
- [ ] Install dependencies: `mcp`, `fastapi`, `uvicorn`, `pandas`, `sqlite3`.
- [ ] Create directory structure:
    - `/mcp_server`: Python MCP server.
    - `/data`: Placeholder for SQLite DB or CSV health exports.
    - `/skills`: Logic for token optimization and data aggregation.

## Phase 2: MCP Server Development
- [ ] Implement `server.py` using the MCP Python SDK.
- [ ] **Tools to implement:**
    - `get_health_summary(date: str)`: Aggregates sleep and activity.
    - `calculate_readiness_score()`: Returns a 1-10 readiness score.
    - `query_raw_logs(query: str)`: Allows LLM to ask specific questions about data points.

## Phase 3: Token Optimization (The "Skill" Layer)
- [ ] Create `summarizer.py` utility.
- [ ] **Strategy:** Pass min, max, and avg heart rate instead of raw 24-hour data to save tokens and improve reasoning speed.

## Phase 4: Cursor & Gemini Integration
- [ ] Configure Cursor to use the local MCP server via `stdio`.
- [ ] Set up `.cursorrules` to define Agent persona and tool-calling constraints.
- [ ] **Test the loop:** "Based on my sleep last night, should I do my 'Deep Work' session now or at 4 PM?"

## Phase 5: Agentic Features
- [ ] Implement a "Plan-and-Execute" loop.
- [ ] **Agent Workflow:**
    - Check health data.
    - Check a mock `todo.json`.
    - Propose a rescheduled calendar.
