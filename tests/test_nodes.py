from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

search_mod = importlib.import_module("src.recipe_agent.nodes.search_recipes")
from src.recipe_agent.nodes.search_recipes import search_recipes
from src.recipe_agent.nodes.rank_recipes import rank_recipes_factory
from src.recipe_agent.nodes.generate_recommendation import generate_recommendation_factory
from src.recipe_agent.state import RecipeAgentState


@pytest.fixture()
def sample_recipes(monkeypatch):
    recipes = [
        {
            "id": 1,
            "name": "Egg Fried Rice",
            "cuisine": "Chinese",
            "cooking_time": 15,
            "dietary": ["vegetarian"],
            "ingredients": ["rice", "egg", "peas"],
        },
        {
            "id": 2,
            "name": "Tofu Buddha Bowl",
            "cuisine": "Asian",
            "cooking_time": 30,
            "dietary": ["vegan"],
            "ingredients": ["tofu", "rice", "veggies"],
        },
    ]
    # Patch global RECIPES_DB used inside search_recipes
    monkeypatch.setattr(search_mod, "RECIPES_DB", recipes)
    return recipes


def test_search_recipes_filters_and_scores(sample_recipes):
    state: RecipeAgentState = {
        "ingredients": ["rice", "egg"],
        "dietary_restrictions": ["vegetarian"],
        "max_cooking_time": 20,
        "cuisine_preference": "chinese",
    }

    out = search_recipes(state)
    matches = out["matched_recipes"]

    assert len(matches) == 1
    m = matches[0]
    assert m["name"] == "Egg Fried Rice"
    # overlap rice+egg plus cuisine bonus (2)
    assert m["score"] == 1 + 1 + 2


def test_rank_recipes_orders_by_llm_response(sample_recipes):
    # Fake LLM that returns only names comma-separated
    class FakeLLM:
        def invoke(self, messages):
            return SimpleNamespace(content="Tofu Buddha Bowl, Egg Fried Rice")

    ranker = rank_recipes_factory(FakeLLM())
    state: RecipeAgentState = {
        "matched_recipes": [
            {**sample_recipes[0], "score": 2},
            {**sample_recipes[1], "score": 1},
        ]
    }

    ranked = ranker(state)["matched_recipes"]
    assert [r["name"] for r in ranked] == ["Tofu Buddha Bowl", "Egg Fried Rice"]


def test_generate_recommendation_requires_ingredients(sample_recipes):
    class FakeLLM:
        def invoke(self, messages):
            return SimpleNamespace(content="stub response")

    generator = generate_recommendation_factory(FakeLLM())

    # No ingredients -> prompt for them
    state: RecipeAgentState = {"matched_recipes": sample_recipes, "ingredients": []}
    out = generator(state)
    assert "Tell me what ingredients" in out["messages"][0].content

    # With ingredients and candidates -> returns formatted suggestion
    state_ok: RecipeAgentState = {
        "matched_recipes": [{**sample_recipes[0], "score": 3}],
        "ingredients": ["rice"],
        "dietary_restrictions": [],
        "max_cooking_time": None,
        "cuisine_preference": None,
    }
    out_ok = generator(state_ok)
    assert out_ok["messages"][0].content == "stub response"
