from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class EmailMessage:
    id: str
    sender: str
    subject: str
    body: str
    unread: bool = True
    attack_category: str | None = None
    expected_attack_tool: str | None = None


@dataclass(frozen=True)
class PlannedToolCall:
    tool_name: str
    args: dict[str, Any]
    reason: str
    source_email_id: str | None = None

    def signature(self) -> tuple[str, tuple[tuple[str, str], ...]]:
        normalized_args = tuple(sorted((key, str(value)) for key, value in self.args.items()))
        return self.tool_name, normalized_args


@dataclass(frozen=True)
class ToolCall:
    run_id: str
    tool_name: str
    args: dict[str, Any]
    authorized: bool
    status: str
    reason: str
    source_email_id: str | None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )


@dataclass
class AgentRun:
    run_id: str
    defense_mode: str
    user_prompt: str
    summary: str
    tool_calls: list[ToolCall]
    blocked_tool_calls: list[ToolCall]
    estimated_prompt_tokens: int
    attack_detected: bool = False

    @classmethod
    def empty(cls, defense_mode: str, user_prompt: str) -> "AgentRun":
        return cls(
            run_id=str(uuid4()),
            defense_mode=defense_mode,
            user_prompt=user_prompt,
            summary="",
            tool_calls=[],
            blocked_tool_calls=[],
            estimated_prompt_tokens=0,
        )
