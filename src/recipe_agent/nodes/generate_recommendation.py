from __future__ import annotations
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage

from ..state import RecipeAgentState

def generate_recommendation_factory(llm: ChatOpenAI):
    def generate_recommendation(state: RecipeAgentState) -> Dict[str, Any]:
        recipes = state.get("matched_recipes", []) or []
        ingredients = state.get("ingredients", []) or []

        if not ingredients:
            return {"messages": [AIMessage(content="Tell me what ingredients you have so I can recommend recipes.")]}
        if not recipes:
            return {"messages": [AIMessage(content="I couldn’t find a matching recipe. Want to relax constraints or add more ingredients?")]}

        prompt = f"""
You are a friendly cooking assistant.

User preferences:
- Ingredients: {state.get("ingredients", [])}
- Dietary restrictions: {state.get("dietary_restrictions", [])}
- Max cooking time: {state.get("max_cooking_time", None)}
- Cuisine preference: {state.get("cuisine_preference", None)}

Candidate recipes (use ONLY these, do not invent new recipes):
{recipes}

Task:
1) Pick the BEST 3 recipes from the candidates for this user.
2) Write the final response EXACTLY in this format:

Based on your ingredients and preferences, here are 3 recipes:
1. <name> (<time> min) - <cuisine>
2. <name> (<time> min) - <cuisine>
3. <name> (<time> min) - <cuisine>
Which one would you like the full recipe for?

No extra text. No explanations. Only the formatted response.
"""
        response = llm.invoke([SystemMessage(content=prompt)])
        return {"messages": [AIMessage(content=response.content)]}

    return generate_recommendation
