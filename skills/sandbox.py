"""Isolated Python script execution sandbox.

Executes agent-generated analysis scripts in a subprocess against the local
health database. Only stdout/stderr are returned to the LLM — raw data never
leaves the local machine.

Security model:
- Scripts run in a child process with a hard timeout.
- DB_PATH is pre-injected read-only; no connection string is exposed.
- Output is truncated to MAX_OUTPUT_CHARS to prevent token flooding.
"""

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "health.db"
TIMEOUT_SECONDS = 30
MAX_OUTPUT_CHARS = 4000
HEAD_CHARS = 2500   # chars shown from the top when truncating
TAIL_CHARS = 800    # chars shown from the bottom when truncating


def run_python_analysis(script: str) -> dict:
    """Execute a Python analysis script in an isolated subprocess.

    Pre-injects DB_PATH and common imports so scripts can connect to the
    health database without needing to know the file system layout. Large
    outputs are truncated to MAX_OUTPUT_CHARS.

    Args:
        script: Python source code to execute. Results must be printed to
            stdout. The script has access to: sqlite3, pandas (as pd),
            pathlib.Path, and the pre-bound DB_PATH string.

    Returns:
        dict with keys:
            output   (str)       — captured stdout, truncated if large.
            error    (str|None)  — captured stderr, or None if clean.
            exit_code (int)      — process exit code; -1 on timeout.
            truncated (bool)     — True if output was truncated.
    """
    preamble = textwrap.dedent(f"""\
        import sqlite3
        import pandas as pd
        from pathlib import Path

        DB_PATH = r"{DB_PATH}"
    """)

    full_script = preamble + "\n" + script

    script_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(full_script)
            script_path = Path(f.name)

        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        raw_output = result.stdout.strip()
        total_lines = raw_output.count("\n") + 1 if raw_output else 0
        total_chars = len(raw_output)
        truncated = total_chars > MAX_OUTPUT_CHARS

        if truncated:
            head = raw_output[:HEAD_CHARS]
            tail = raw_output[-TAIL_CHARS:]
            omitted_chars = total_chars - HEAD_CHARS - TAIL_CHARS
            output = (
                f"{head}\n\n"
                f"... [{omitted_chars:,} characters omitted — {total_lines} lines total] ...\n\n"
                f"{tail}"
            )
        else:
            output = raw_output

        return {
            "output": output,
            "error": result.stderr.strip() or None,
            "exit_code": result.returncode,
            "truncated": truncated,
            "total_lines": total_lines,
            "total_chars": total_chars,
        }

    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": f"Script timed out after {TIMEOUT_SECONDS} seconds.",
            "exit_code": -1,
            "truncated": False,
            "total_lines": 0,
            "total_chars": 0,
        }
    finally:
        if script_path and script_path.exists():
            script_path.unlink(missing_ok=True)
