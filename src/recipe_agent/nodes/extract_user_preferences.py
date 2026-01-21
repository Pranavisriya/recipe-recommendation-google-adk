from __future__ import annotations
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from ..schemas import UserInput
from ..prompts import EXTRACTION_SYSTEM
from ..state import RecipeAgentState

def build_extractor(llm: ChatOpenAI):
    return llm.with_structured_output(UserInput)

def extract_user_preferences_factory(llm: ChatOpenAI):
    extractor = build_extractor(llm)

    def extract_user_preferences(state: RecipeAgentState) -> Dict[str, Any]:
        messages = [{"role": "system", "content": EXTRACTION_SYSTEM}] + list(state["messages"])
        response = extractor.invoke(messages)
        return {
            "ingredients": response.ingredients,
            "dietary_restrictions": response.dietary_restrictions,
            "max_cooking_time": response.max_cooking_time,
            "cuisine_preference": response.cuisine_preference,
        }

    return extract_user_preferences
