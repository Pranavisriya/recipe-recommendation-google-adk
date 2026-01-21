from __future__ import annotations

from langchain_core.messages import BaseMessage

from ..state import RecipeAgentState
from ..prompts import EXTRACTION_SYSTEM


def extract_user_preferences(
    state: RecipeAgentState,
    *,
    extractor, 
) -> RecipeAgentState:
    """
    Extract structured preferences from the latest conversation messages.
    """
    messages = [{"role": "system", "content": EXTRACTION_SYSTEM}] + list(state["messages"])
    response = extractor.invoke(messages)

    return {
        "ingredients": response.ingredients,
        "dietary_restrictions": response.dietary_restrictions,
        "max_cooking_time": response.max_cooking_time,
        "cuisine_preference": response.cuisine_preference,
    }
