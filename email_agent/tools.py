from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import EmailMessage, PlannedToolCall, ToolCall


class EmailToolbox:
    def __init__(self, emails: list[EmailMessage], allowed_tools: set[str], run_id: str):
        self._emails = {email.id: email for email in emails}
        self.allowed_tools = allowed_tools
        self.run_id = run_id
        self.sent_messages: list[dict[str, Any]] = []
        self.forwarded_messages: list[dict[str, Any]] = []
        self.deleted_email_ids: list[str] = []
        self.logs: list[ToolCall] = []

    def execute(self, planned: PlannedToolCall) -> Any:
        authorized = planned.tool_name in self.allowed_tools
        if planned.tool_name == "read_emails":
            result = self.read_emails(**planned.args)
        elif planned.tool_name == "send_email":
            result = self.send_email(**planned.args)
        elif planned.tool_name == "forward_email":
            result = self.forward_email(**planned.args)
        elif planned.tool_name == "delete_email":
            result = self.delete_email(**planned.args)
        else:
            raise ValueError(f"Unknown tool: {planned.tool_name}")

        self.logs.append(
            ToolCall(
                run_id=self.run_id,
                tool_name=planned.tool_name,
                args=deepcopy(planned.args),
                authorized=authorized,
                status="executed",
                reason=planned.reason,
                source_email_id=planned.source_email_id,
            )
        )
        return result

    def read_emails(self, unread_only: bool = True) -> list[dict[str, Any]]:
        emails = [
            email
            for email in self._emails.values()
            if not unread_only or email.unread
        ]
        return [
            {
                "id": email.id,
                "sender": email.sender,
                "subject": email.subject,
                "body": email.body,
                "unread": email.unread,
            }
            for email in emails
        ]

    def send_email(self, to: str, subject: str, body: str) -> dict[str, Any]:
        message = {"to": to, "subject": subject, "body": body}
        self.sent_messages.append(message)
        return {"sent": True, **message}

    def forward_email(self, email_id: str, to: str, note: str = "") -> dict[str, Any]:
        email = self._emails.get(email_id)
        forwarded = {
            "email_id": email_id,
            "to": to,
            "note": note,
            "original_subject": email.subject if email else None,
        }
        self.forwarded_messages.append(forwarded)
        return {"forwarded": email is not None, **forwarded}

    def delete_email(self, email_id: str) -> dict[str, Any]:
        if email_id in self._emails:
            self.deleted_email_ids.append(email_id)
            return {"deleted": True, "email_id": email_id}
        return {"deleted": False, "email_id": email_id}


def blocked_tool_call(run_id: str, planned: PlannedToolCall, reason: str) -> ToolCall:
    return ToolCall(
        run_id=run_id,
        tool_name=planned.tool_name,
        args=deepcopy(planned.args),
        authorized=False,
        status="blocked",
        reason=reason,
        source_email_id=planned.source_email_id,
    )
