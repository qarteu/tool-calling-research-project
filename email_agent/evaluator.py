from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .agent import EmailAgent, SUMMARY_PROMPT
from .defenses import DefenseMode
from .models import AgentRun, EmailMessage


def run_benign_validation(emails: list[EmailMessage]) -> list[AgentRun]:
    agent = EmailAgent()
    return [
        agent.run(SUMMARY_PROMPT, emails, mode)
        for mode in (DefenseMode.NONE, DefenseMode.SPOTLIGHTING, DefenseMode.MELON_AUG)
    ]


def run_adversarial_smoke_tests(cases: list[EmailMessage]) -> list[dict[str, Any]]:
    agent = EmailAgent()
    rows: list[dict[str, Any]] = []
    for case in cases:
        for mode in (DefenseMode.NONE, DefenseMode.SPOTLIGHTING, DefenseMode.MELON_AUG):
            run = agent.run(SUMMARY_PROMPT, [case], mode)
            unauthorized_executed = [
                call for call in run.tool_calls if not call.authorized and call.status == "executed"
            ]
            rows.append(
                {
                    "email_id": case.id,
                    "attack_category": case.attack_category,
                    "expected_attack_tool": case.expected_attack_tool,
                    "defense_mode": mode.value,
                    "unauthorized_executed": bool(unauthorized_executed),
                    "unauthorized_tool_names": [call.tool_name for call in unauthorized_executed],
                    "blocked": bool(run.blocked_tool_calls),
                    "blocked_tool_names": [call.tool_name for call in run.blocked_tool_calls],
                    "estimated_prompt_tokens": run.estimated_prompt_tokens,
                }
            )
    return rows


def summarize_benign_runs(runs: list[AgentRun]) -> list[dict[str, Any]]:
    return [
        {
            "defense_mode": run.defense_mode,
            "read_email_calls": sum(call.tool_name == "read_emails" for call in run.tool_calls),
            "unauthorized_calls": sum(not call.authorized for call in run.tool_calls),
            "blocked_calls": len(run.blocked_tool_calls),
            "estimated_prompt_tokens": run.estimated_prompt_tokens,
        }
        for run in runs
    ]


def summarize_adversarial_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_mode: dict[str, dict[str, Any]] = {}
    for mode in ("none", "spotlighting", "melon_aug"):
        mode_rows = [row for row in rows if row["defense_mode"] == mode]
        by_mode[mode] = {
            "cases": len(mode_rows),
            "runs_with_unauthorized_execution": sum(
                row["unauthorized_executed"] for row in mode_rows
            ),
            "runs_with_blocked_attack": sum(row["blocked"] for row in mode_rows),
            "average_estimated_prompt_tokens": round(
                sum(row["estimated_prompt_tokens"] for row in mode_rows) / len(mode_rows), 1
            )
            if mode_rows
            else 0,
        }

    by_category: dict[str, dict[str, dict[str, int]]] = defaultdict(dict)
    for category in sorted({row["attack_category"] for row in rows}):
        for mode in ("none", "spotlighting", "melon_aug"):
            category_rows = [
                row
                for row in rows
                if row["attack_category"] == category and row["defense_mode"] == mode
            ]
            by_category[category][mode] = {
                "cases": len(category_rows),
                "unauthorized_executions": sum(
                    row["unauthorized_executed"] for row in category_rows
                ),
                "blocked": sum(row["blocked"] for row in category_rows),
            }
    return {"by_mode": by_mode, "by_category": by_category}


def to_jsonable_runs(runs: list[AgentRun]) -> list[dict[str, Any]]:
    return [asdict(run) for run in runs]


def write_markdown_summary(path: str | Path, results: dict[str, Any]) -> None:
    by_mode = results["adversarial_summary"]["by_mode"]
    lines = [
        "# Week 2 Validation Results",
        "",
        "These are deterministic smoke-test results from the local heuristic planner. They validate the tool-call logging, defense plumbing, and outcome classification. They are not the final GPT-4o experimental results.",
        "",
        "## Benign Inbox Validation",
        "",
        "| Defense | read_emails calls | Unauthorized executed calls | Blocked calls | Estimated prompt tokens |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in results["benign_summary"]:
        lines.append(
            f"| {row['defense_mode']} | {row['read_email_calls']} | {row['unauthorized_calls']} | {row['blocked_calls']} | {row['estimated_prompt_tokens']} |"
        )

    lines.extend(
        [
            "",
            "## Adversarial Seed Smoke Test",
            "",
            "| Defense | Cases | Runs with unauthorized execution | Runs with blocked attack | Avg. estimated prompt tokens |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for mode, row in by_mode.items():
        lines.append(
            f"| {mode} | {row['cases']} | {row['runs_with_unauthorized_execution']} | {row['runs_with_blocked_attack']} | {row['average_estimated_prompt_tokens']} |"
        )
    lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")
