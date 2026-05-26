# Evaluating Indirect Prompt Injection in Tool-Calling LLM Email Agents

This repository contains the Week 2 implementation for the project. The goal is
to evaluate whether an email assistant asked to summarize unread emails can be
tricked into unauthorized tool use by malicious instructions hidden inside email
content.

## Week 2 Scope

- Built a Python email-agent harness with a simulated inbox.
- Implemented four tools: `read_emails`, `send_email`, `forward_email`, and
  `delete_email`.
- Added tool-call logging with authorization labels.
- Implemented Spotlighting-style prompt marking for untrusted email content.
- Implemented MELON-Aug-style masked re-execution detection for unauthorized
  tool calls.
- Added benign inbox validation and 12 adversarial seed emails for smoke tests.

The local planner is deterministic and exists to validate the framework without
using model budget. Final experimental measurements should replace it with the
fixed GPT-4o tool-calling agent.

## Run Validation

```bash
python -m unittest discover -s tests
python scripts/run_week2_validation.py
```

Outputs are written to:

- `results/week2_validation_results.json`
- `results/week2_validation_summary.md`
