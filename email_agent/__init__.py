"""Week 2 email-agent implementation for indirect prompt injection evaluation."""

from .agent import EmailAgent, HeuristicPlanner
from .defenses import DefenseMode
from .models import AgentRun, EmailMessage, PlannedToolCall, ToolCall

__all__ = [
    "AgentRun",
    "DefenseMode",
    "EmailAgent",
    "EmailMessage",
    "HeuristicPlanner",
    "PlannedToolCall",
    "ToolCall",
]
