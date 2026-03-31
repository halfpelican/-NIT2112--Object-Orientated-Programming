# Prompt: Generate a Practical Demonstration

Use this prompt to have the agent produce a fully runnable, lecture-ready demo — including
environment setup, annotated code, expected output, and discussion questions.

---

## How to Use

1. Open Copilot Chat (`Ctrl+Alt+I`) → Agent mode.
2. Paste the section below, filling in your values, and send.

---

Create a practical demonstration for the following:

- **Concept to demonstrate**: {{CONCEPT}}
  *(e.g., "overfitting vs underfitting using polynomial regression",
    "feature scaling impact on KNN accuracy")*

- **Difficulty level**: {{LEVEL}}
  *(beginner | intermediate | advanced)*

- **Target duration** (live lecture demo): {{DURATION}}
  *(e.g., "15 minutes")*

- **Libraries to use**: {{LIBRARIES}}
  *(e.g., "pandas, scikit-learn, matplotlib" — or "leave blank for defaults")*

- **Dataset**: {{DATASET}}
  *(e.g., "California Housing from scikit-learn", "auto-generate synthetic data")*

- **Output format**: {{FORMAT}}
  *(Python script | Jupyter notebook outline | both)*

- **Additional instructions** (optional): {{NOTES}}
  *(e.g., "show a before/after comparison", "include a PowerShell setup block students can
    copy-paste to get running immediately")*

Produce the full demonstration including: narrative intro, PowerShell environment setup,
annotated script, expected output snippet, common pitfalls, and at least 3 discussion questions.
