# Prompt: Design a Data Science Assignment

Use this prompt in GitHub Copilot Chat (agent mode) to generate a complete, ready-to-distribute
assignment. Fill in the variables below before submitting.

---

## How to Use

1. Open Copilot Chat in VS Code (`Ctrl+Alt+I`).
2. Switch to **Agent mode** (click the sparkle icon → "Ask").
3. Paste this file's contents (from the `---` below) into the chat, filling in your values.

---

Design a data science assignment with the following parameters:

- **Topic**: {{TOPIC}}
  *(e.g., "logistic regression for binary classification", "time-series forecasting with ARIMA")*

- **Unit week**: {{WEEK_NUMBER}}
  *(e.g., 4 — used to calibrate difficulty)*

- **Estimated student hours**: {{HOURS}}
  *(e.g., 8 hours)*

- **Preferred dataset**: {{DATASET_OR_AUTO}}
  *(e.g., "Titanic", "leave blank for a recommendation")*

- **Deliverables**: {{DELIVERABLES}}
  *(e.g., "Python script + 2-page PDF report", "Jupyter notebook only")*

- **Special constraints** (optional): {{CONSTRAINTS}}
  *(e.g., "no scikit-learn — implement from scratch", "must include a visualisation dashboard")*

Please produce the full assignment specification including learning objectives, task breakdown,
dataset instructions, submission checklist, and marking rubric.
