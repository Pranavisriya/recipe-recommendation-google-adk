from __future__ import annotations

"""
Runtime helpers that mirror the interactive workflow from
`experiments/adk_practise.ipynb`, but packaged as reusable Python code.

Key utilities:
- `create_session` to start an ADK session.
- `call_adk` to send a user query through the recipe manager agent and get the
  final assistant text.
"""

import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .app import root_agent

# Load environment variables (OPENAI_API_KEY, GOOGLE_API_KEY, etc.)
load_dotenv()

# ---------------------- ADK runtime wiring ----------------------
APP_NAME = "recipe_app"
_session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=_session_service,
)


async def create_session(user_id: Optional[str] = None):
    """
    Create and return a new ADK session. If user_id is not provided, a
    short random ID is used.
    """
    uid = user_id or f"user_{uuid.uuid4().hex[:8]}"
    return await _session_service.create_session(app_name=APP_NAME, user_id=uid)


async def call_adk(query: str, *, session_id: str, user_id: str) -> str:
    """
    Send a user query through the recipe_manager agent and return the final
    assistant message text (mirrors the notebook's call_adk).
    """
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_text: Optional[str] = None
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_text = event.content.parts[0].text
            else:
                final_text = event.error_message or "No final text returned."
            break

    return final_text or "No response."
