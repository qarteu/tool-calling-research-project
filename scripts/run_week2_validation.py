from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from email_agent.datasets import load_email_messages
from email_agent.evaluator import (
    run_adversarial_smoke_tests,
    run_benign_validation,
    summarize_adversarial_rows,
    summarize_benign_runs,
    to_jsonable_runs,
    write_markdown_summary,
)


def main() -> None:
    benign = load_email_messages(ROOT / "data" / "benign_inbox.json")
    adversarial = load_email_messages(ROOT / "data" / "adversarial_seed.json")

    benign_runs = run_benign_validation(benign)
    adversarial_rows = run_adversarial_smoke_tests(adversarial)

    results = {
        "note": (
            "Week 2 local validation results from deterministic heuristic planner; "
            "not final GPT-4o experimental measurements."
        ),
        "benign_runs": to_jsonable_runs(benign_runs),
        "benign_summary": summarize_benign_runs(benign_runs),
        "adversarial_rows": adversarial_rows,
        "adversarial_summary": summarize_adversarial_rows(adversarial_rows),
    }

    output_dir = ROOT / "results"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "week2_validation_results.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )
    write_markdown_summary(output_dir / "week2_validation_summary.md", results)

    print(json.dumps(results["adversarial_summary"]["by_mode"], indent=2))


if __name__ == "__main__":
    main()
