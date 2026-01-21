from __future__ import annotations
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from ..state import RecipeAgentState

def rank_recipes_factory(llm: ChatOpenAI):
    def rank_recipes(state: RecipeAgentState) -> Dict[str, Any]:
        recipes = state.get("matched_recipes", []) or []
        if not recipes:
            return {"matched_recipes": []}

        prompt = (
            "You are a cooking assistant.\n"
            "Rank the following recipes from best to worst for the user.\n\n"
            "User preferences:\n"
            f"- Ingredients: {state.get('ingredients', [])}\n"
            f"- Dietary: {state.get('dietary_restrictions', [])}\n"
            f"- Max time: {state.get('max_cooking_time', None)}\n"
            f"- Cuisine: {state.get('cuisine_preference', None)}\n\n"
            "Recipes:\n"
        )

        for r in recipes:
            prompt += (
                f"- {r['name']} | cuisine={r['cuisine']} | "
                f"time={r['cooking_time']} | score={r['score']}\n"
            )

        prompt += "\nReturn ONLY a comma-separated list of recipe names ranked from best to worst."
        response = llm.invoke([SystemMessage(content=prompt)])

        ranked_names = [x.strip() for x in response.content.split(",") if x.strip()]
        name_to_recipe = {r["name"]: r for r in recipes}
        ranked = [name_to_recipe[n] for n in ranked_names if n in name_to_recipe]

        remaining = [r for r in recipes if r["name"] not in ranked_names]
        remaining = sorted(remaining, key=lambda r: r["score"], reverse=True)

        return {"matched_recipes": ranked + remaining}

    return rank_recipes
