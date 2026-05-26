from __future__ import annotations

from enum import StrEnum

from .models import EmailMessage, PlannedToolCall


class DefenseMode(StrEnum):
    NONE = "none"
    SPOTLIGHTING = "spotlighting"
    MELON_AUG = "melon_aug"


def spotlight_email(email: EmailMessage) -> str:
    lines = email.body.splitlines() or [email.body]
    quoted_body = "\n".join(f"UNTRUSTED_EMAIL_DATA: {line}" for line in lines)
    return (
        f"BEGIN_UNTRUSTED_EMAIL id={email.id} sender={email.sender} subject={email.subject}\n"
        f"{quoted_body}\n"
        "END_UNTRUSTED_EMAIL"
    )


def render_inbox_for_prompt(emails: list[EmailMessage], defense_mode: DefenseMode) -> str:
    if defense_mode in {DefenseMode.SPOTLIGHTING, DefenseMode.MELON_AUG}:
        return "\n\n".join(spotlight_email(email) for email in emails if email.unread)

    return "\n\n".join(
        (
            f"Email id={email.id}\n"
            f"From: {email.sender}\n"
            f"Subject: {email.subject}\n"
            f"Body: {email.body}"
        )
        for email in emails
        if email.unread
    )


def mask_user_prompt(_: str) -> str:
    return "[USER_PROMPT_MASKED]"


def find_melon_blocked_calls(
    primary_plan: list[PlannedToolCall],
    masked_plan: list[PlannedToolCall],
    allowed_tools: set[str],
) -> set[tuple[str, tuple[tuple[str, str], ...]]]:
    """Flag unauthorized actions that still appear when the user prompt is masked."""
    masked_unauthorized = {
        planned.signature()
        for planned in masked_plan
        if planned.tool_name not in allowed_tools
    }
    return {
        planned.signature()
        for planned in primary_plan
        if planned.tool_name not in allowed_tools and planned.signature() in masked_unauthorized
    }
