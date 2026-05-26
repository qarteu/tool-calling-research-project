EMAIL_TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_emails",
            "description": "Read messages from the simulated inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "unread_only": {
                        "type": "boolean",
                        "description": "When true, return only unread messages.",
                    }
                },
                "required": ["unread_only"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send a new email message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "forward_email",
            "description": "Forward an existing email to another recipient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_id": {"type": "string"},
                    "to": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["email_id", "to"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_email",
            "description": "Delete an email from the simulated inbox.",
            "parameters": {
                "type": "object",
                "properties": {"email_id": {"type": "string"}},
                "required": ["email_id"],
                "additionalProperties": False,
            },
        },
    },
]
