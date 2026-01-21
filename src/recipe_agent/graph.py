from __future__ import annotations
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from .state import RecipeAgentState
from .nodes.search_recipes import search_recipes
from .nodes.extract_user_preferences import extract_user_preferences_factory
from .nodes.rank_recipes import rank_recipes_factory
from .nodes.generate_recommendation import generate_recommendation_factory


load_dotenv()

def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0,
    )

def build_recipe_graph():
    llm = get_llm()

    g = StateGraph(RecipeAgentState)
    g.add_node("extract_user_preferences", extract_user_preferences_factory(llm))
    g.add_node("search_recipes", search_recipes)
    g.add_node("rank_recipes", rank_recipes_factory(llm))
    g.add_node("generate_recommendation", generate_recommendation_factory(llm))


    g.set_entry_point("extract_user_preferences")
    g.add_edge("extract_user_preferences", "search_recipes")
    g.add_edge("search_recipes", "rank_recipes")
    g.add_edge("rank_recipes", "generate_recommendation")
    g.add_edge("generate_recommendation", END)

    return g.compile()
