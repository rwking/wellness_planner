"""Observable Plot chart generation skill.

Produces self-contained HTML files that embed data as JSON and render
interactive charts via Observable Plot loaded from CDN. The LLM agent
provides data + a declarative spec; this skill handles all HTML boilerplate.

Output files are saved to data/charts/. Only the file path is returned to
the agent — raw data never re-enters the chat context.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Literal

CHARTS_DIR = Path(__file__).resolve().parent.parent / "data" / "charts"

MarkType = Literal["line", "dot", "bar", "area", "boxX"]

_OBSERVABLE_PLOT_CDN = "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6"
_D3_CDN = "https://cdn.jsdelivr.net/npm/d3@7"

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <script src="{d3_cdn}"></script>
  <script src="{plot_cdn}"></script>
  <style>
    body {{ font-family: system-ui, sans-serif; padding: 2rem; background: #fafafa; }}
    h2   {{ color: #333; margin-bottom: 1rem; }}
    #chart svg {{ max-width: 100%; height: auto; }}
  </style>
</head>
<body>
  <h2>{title}</h2>
  <div id="chart"></div>
  <script>
    const data = {data_json};

    const plot = Plot.plot({{
      marginLeft: 60,
      marginBottom: 50,
      x: {{ label: "{x_label}", tickRotate: -30 }},
      y: {{ label: "{y_label}", grid: true }},
      marks: [
        {mark_expr},
        Plot.ruleY([0])
      ]
    }});

    document.getElementById("chart").appendChild(plot);
  </script>
</body>
</html>
"""

_MARK_TEMPLATES: dict[str, str] = {
    "line":  'Plot.line(data, {{ x: "{x}", y: "{y}", stroke: "#4f7be8", strokeWidth: 2 }})',
    "dot":   'Plot.dot(data,  {{ x: "{x}", y: "{y}", fill: "#4f7be8", r: 4 }})',
    "bar":   'Plot.barY(data, {{ x: "{x}", y: "{y}", fill: "#4f7be8" }})',
    "area":  'Plot.areaY(data, {{ x: "{x}", y: "{y}", fill: "#4f7be8", fillOpacity: 0.3 }})',
    "boxX":  'Plot.boxX(data, {{ x: "{y}", y: "{x}", fill: "#4f7be8" }})',
}


def generate_chart(
    data: list[dict],
    title: str,
    x: str,
    y: str,
    mark_type: MarkType = "line",
    filename: str | None = None,
) -> dict:
    """Generate a self-contained Observable Plot HTML chart from tabular data.

    Args:
        data: List of dicts, each representing one data point. Must contain
            at least the columns named by `x` and `y`.
        title: Human-readable chart title shown as an H2 heading.
        x: Column name to use for the x-axis.
        y: Column name to use for the y-axis.
        mark_type: Plot mark to use. One of: "line", "dot", "bar", "area", "boxX".
            Defaults to "line".
        filename: Optional output filename (without path). Auto-generated from
            title + timestamp if omitted.

    Returns:
        dict with keys:
            path (str)   — absolute path to the generated HTML file.
            url  (str)   — file:// URL for quick browser open.
            rows (int)   — number of data points rendered.
    """
    if not data:
        return {"error": "data list is empty — no chart generated."}

    if x not in data[0] or y not in data[0]:
        missing = [col for col in (x, y) if col not in data[0]]
        return {"error": f"Column(s) not found in data: {missing}. Available: {list(data[0].keys())}"}

    if mark_type not in _MARK_TEMPLATES:
        return {"error": f"Unknown mark_type '{mark_type}'. Choose from: {list(_MARK_TEMPLATES)}"}

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    if not filename:
        safe_title = re.sub(r"[^\w\-]", "_", title.lower())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.html"

    mark_expr = _MARK_TEMPLATES[mark_type].format(x=x, y=y)

    html = _HTML_TEMPLATE.format(
        title=title,
        data_json=json.dumps(data),
        x_label=x.replace("_", " ").title(),
        y_label=y.replace("_", " ").title(),
        mark_expr=mark_expr,
        d3_cdn=_D3_CDN,
        plot_cdn=_OBSERVABLE_PLOT_CDN,
    )

    out_path = CHARTS_DIR / filename
    out_path.write_text(html, encoding="utf-8")

    return {
        "path": str(out_path),
        "url": out_path.as_uri(),
        "rows": len(data),
    }
