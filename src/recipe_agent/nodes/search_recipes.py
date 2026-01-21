from __future__ import annotations
from typing import Dict, Any

from ..state import RecipeAgentState
from ..data.recipes_db import RECIPES_DB

def search_recipes(state: RecipeAgentState) -> Dict[str, Any]:
    ingredients = set(i.lower() for i in state.get("ingredients", []))
    dietary = set(state.get("dietary_restrictions", []))
    max_time = state.get("max_cooking_time", None)
    cuisine_pref = (state.get("cuisine_preference", "") or "").lower()

    matches = []
    for r in RECIPES_DB:
        r_ings = set(x.lower() for x in r["ingredients"])

        if dietary and (not dietary.issubset(set(r["dietary"]))):
            continue
        if max_time is not None and r["cooking_time"] > max_time:
            continue

        overlap = len(ingredients.intersection(r_ings)) if ingredients else 0
        if ingredients and overlap == 0:
            continue

        score = overlap + (2 if cuisine_pref and r["cuisine"].lower() == cuisine_pref else 0)
        matches.append({**r, "score": score})

    return {"matched_recipes": matches}
