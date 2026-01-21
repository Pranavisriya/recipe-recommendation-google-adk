from __future__ import annotations
from google.adk import Agent
from langchain_core.messages import HumanMessage

from .graph import build_recipe_graph
from .data.recipes_db import (
    get_best_ingredient_prices,
    authenticate_wallet,
    get_wallet_balance,
    deduct_wallet,
)

# Build LangGraph once
_graph = build_recipe_graph()

def recommend_recipes(user_message: str) -> str:
    """
    ADK tool wrapper: calls LangGraph recipe manager and returns final assistant message.
    """
    out = _graph.invoke({"messages": [HumanMessage(content=user_message)]})
    msgs = out.get("messages") or []
    return msgs[-1].content if msgs else "No response."

# Sub agents
recipe_agent = Agent(
    name="recipe_agent",
    description="Recipe recommendations (calls LangGraph recipe manager).",
    tools=[recommend_recipes],
    instruction="""
Use recommend_recipes(user_message) to generate recipe recommendations.
Do not invent recipes outside the CSV database.
Return the tool output directly to the user.
"""
)

ingredient_price_agent = Agent(
    name="ingredient_price_agent",
    description="Find best store prices for ingredients using CSV.",
    tools=[get_best_ingredient_prices],
    instruction="""
Extract ingredient names from the user request and call get_best_ingredient_prices(ingredients).
Do not guess prices if not present in CSV.
"""
)

wallet_agent = Agent(
    name="wallet_agent",
    description="Authenticate and manage wallet balance using CSV.",
    tools=[authenticate_wallet, get_wallet_balance, deduct_wallet],
    instruction="""
Ask for user_id and PIN if needed.
Never deduct without explicit user confirmation.
Check balance before deduction.
"""
)

# Required by ADK runtime
root_agent = Agent(
    name="recipe_manager",
    description="Routes between recipe, prices, and wallet agents.",
    sub_agents=[recipe_agent, ingredient_price_agent, wallet_agent],
    instruction="""
You are the recipe manager.

Routing:
- If user asks for recipes / cooking suggestions -> recipe_agent
- If user asks about ingredient prices / where to buy -> ingredient_price_agent
- If user asks about wallet / balance / purchase / pin -> wallet_agent

Be grounded: do not invent recipes, prices, or wallet data.
"""
)
