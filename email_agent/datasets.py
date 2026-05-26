from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import EmailMessage


def load_email_messages(path: str | Path) -> list[EmailMessage]:
    with Path(path).open("r", encoding="utf-8") as file:
        raw_messages = json.load(file)
    return [email_from_dict(message) for message in raw_messages]


def email_from_dict(message: dict[str, Any]) -> EmailMessage:
    return EmailMessage(
        id=message["id"],
        sender=message["sender"],
        subject=message["subject"],
        body=message["body"],
        unread=message.get("unread", True),
        attack_category=message.get("attack_category"),
        expected_attack_tool=message.get("expected_attack_tool"),
    )


def group_adversarial_cases(messages: list[EmailMessage]) -> list[EmailMessage]:
    return [message for message in messages if message.attack_category]
