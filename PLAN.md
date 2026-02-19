# Phase 1: The "Sandbox" Tool (Execution)

The core of an analytical agent is the ability to run code. We will extend your Python MCP server to include a run_analysis tool.

## Objectives

- Create a run_analysis tool that accepts a Python script as a string.
- Use a subprocess to execute the code in your local environment.
- Capture stdout and stderr to return to Gemini.

## Key Learning

You will see how Agentic Loops handle errors. If the script fails, Gemini reads the error, modifies the code, and tries again (Auto-debugging).

---

# Phase 2: The "Data Map" (Contextual Awareness)

Analytical agents fail if they don't understand the schema. We need to give Gemini a "Mental Model" of your data without sending the data itself.

## Objectives

- **Schema Discovery Tool:** Create a tool `get_data_dictionary` that returns column names, data types, and a few sample values.
- **Rules Update:** Update your `.cursorrules` to instruct the agent to always check the schema before writing analysis code.

---

# Phase 3: The "Discovery" Prompting Strategy

Analytics requires a different persona. We move from "Chatbot" to "Data Scientist."

## Objectives

- **Planning Loop:** Configure the agent to write a "Research Plan" first.
  - Step 1: Identify variables.
  - Step 2: Clean/Normalize (e.g., date formats).
  - Step 3: Statistical test (Correlation, Regression).
- **Visualization:** Add a "Skill" that allows the agent to generate plots using [Observable Plot](https://observablehq.com/plot/). The skill produces a self-contained HTML file embedding the chart and returns the local file path.

---

# Phase 4: Token Optimization & State

Instead of sending every analysis result back into the main chat, we keep the data "Local-First."

## Objectives

- **Summarization Skill:** Ensure the run_analysis tool logic includes a step to summarize large outputs.
- **Memory:** Implement a simple JSON-based "Fact Store" where the agent saves discovered insights (e.g., "User's peak energy is 10 AM") so it doesn't have to re-run the analysis every time.
