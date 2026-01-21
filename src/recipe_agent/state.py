from __future__ import annotations
import operator
from typing import Annotated, Sequence, TypedDict, Optional, List

from langchain_core.messages import BaseMessage

class RecipeAgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], operator.add]

    ingredients: List[str]
    dietary_restrictions: List[str]
    max_cooking_time: Optional[int]  # minutes
    cuisine_preference: Optional[str]

    matched_recipes: List[dict]
