"""
Conversation Repository — db/conversation_repo.py
Handles all persistence for users, conversations, and messages.

.NET analogy:
  This file ≈ a Repository class (IConversationRepository)
  Each method ≈ a repository method like GetByIdAsync / AddAsync
  pyodbc connection ≈ SqlConnection / DbContext
"""

import json
import uuid
from datetime import datetime, timezone

import pyodbc

from config.settings import DB_CONNECTION_STRING


def _connect() -> pyodbc.Connection:
    return pyodbc.connect(DB_CONNECTION_STRING, autocommit=True)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def ensure_user(user_id: str, display_name: str = "Default User") -> None:
    """Insert user if not exists. .NET analogy: FirstOrCreate pattern."""
    with _connect() as conn:
        conn.execute(
            """
            IF NOT EXISTS (SELECT 1 FROM users WHERE user_id = ?)
                INSERT INTO users (user_id, display_name) VALUES (?, ?)
            """,
            user_id, user_id, display_name,
        )


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

def create_conversation(user_id: str, session_id: str, first_message: str) -> str:
    """
    Creates a new conversation row and returns its conversation_id.
    Title is derived from the first user message (truncated to 60 chars).
    """
    conversation_id = str(uuid.uuid4())
    title = first_message[:60] + ("..." if len(first_message) > 60 else "")

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO conversations (conversation_id, user_id, session_id, title)
            VALUES (?, ?, ?, ?)
            """,
            conversation_id, user_id, session_id, title,
        )

    return conversation_id


def get_conversations(user_id: str) -> list[dict]:
    """
    Returns all conversations for a user ordered by most recent activity.
    Used to populate the left-panel sidebar.
    """
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT conversation_id, session_id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = ?
            ORDER BY updated_at DESC
            """,
            user_id,
        )
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def touch_conversation(conversation_id: str) -> None:
    """Updates updated_at to now — called after every new message."""
    with _connect() as conn:
        conn.execute(
            "UPDATE conversations SET updated_at = GETUTCDATE() WHERE conversation_id = ?",
            conversation_id,
        )


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def save_message(
    conversation_id: str,
    role: str,
    content: str,
    tool_calls: list | None = None,
) -> None:
    """
    Persists a single message turn.
    tool_calls is serialized to JSON string (matches AgentResponse.tool_calls shape).
    """
    tool_calls_json = json.dumps(tool_calls) if tool_calls else None

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content, tool_calls)
            VALUES (?, ?, ?, ?)
            """,
            conversation_id, role, content, tool_calls_json,
        )

    touch_conversation(conversation_id)


def get_messages(conversation_id: str) -> list[dict]:
    """
    Returns all messages for a conversation in chronological order.
    Used when user clicks a conversation in the sidebar to reload it.
    """
    with _connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT message_id, role, content, tool_calls, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            conversation_id,
        )
        columns = [col[0] for col in cursor.description]
        rows = []
        for row in cursor.fetchall():
            record = dict(zip(columns, row))
            if record["tool_calls"]:
                record["tool_calls"] = json.loads(record["tool_calls"])
            rows.append(record)
        return rows
