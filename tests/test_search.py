import pytest
from src.recipe_agent.nodes.search_recipes import search_recipes
from src.recipe_agent.state import RecipeAgentState


def test_search_recipes_with_ingredients():
    state: RecipeAgentState = {
        "ingredients": ["rice", "vegetables", "beans", "avocado"],
        "dietary_restrictions": [],
        "max_cooking_time": 20,
        "cuisine_preference": None,
    }
    result = search_recipes(state)
    assert "matched_recipes" in result
    recipes = result["matched_recipes"]
    assert len(recipes) > 0
    # Check that all recipes have ingredients overlapping
    for r in recipes:
        assert r["cooking_time"] <= 20
        r_ings = set(x.lower() for x in r["ingredients"])
        user_ings = set(x.lower() for x in state["ingredients"])
        assert len(user_ings.intersection(r_ings)) > 0


def test_search_recipes_no_matches():
    state: RecipeAgentState = {
        "ingredients": ["nonexistent"],
        "dietary_restrictions": [],
        "max_cooking_time": None,
        "cuisine_preference": None,
    }
    result = search_recipes(state)
    assert result["matched_recipes"] == []


def test_search_recipes_with_dietary():
    state: RecipeAgentState = {
        "ingredients": ["rice"],
        "dietary_restrictions": ["vegan"],
        "max_cooking_time": None,
        "cuisine_preference": None,
    }
    result = search_recipes(state)
    recipes = result["matched_recipes"]
    for r in recipes:
        assert "vegan" in r["dietary"]


def test_search_recipes_with_cuisine():
    state: RecipeAgentState = {
        "ingredients": ["rice"],
        "dietary_restrictions": [],
        "max_cooking_time": None,
        "cuisine_preference": "Asian",
    }
    result = search_recipes(state)
    recipes = result["matched_recipes"]
    # Should have higher score for Asian
    asian_recipes = [r for r in recipes if r["cuisine"] == "Asian"]
    if asian_recipes:
        max_score = max(r["score"] for r in recipes)
        assert any(r["score"] == max_score for r in asian_recipes)


def test_search_recipes_with_time_limit():
    state: RecipeAgentState = {
        "ingredients": ["rice"],
        "dietary_restrictions": [],
        "max_cooking_time": 15,
        "cuisine_preference": None,
    }
    result = search_recipes(state)
    recipes = result["matched_recipes"]
    for r in recipes:
        assert r["cooking_time"] <= 15


def test_search_recipes_multiple_dietary():
    state: RecipeAgentState = {
        "ingredients": ["rice"],
        "dietary_restrictions": ["vegan", "gluten-free"],
        "max_cooking_time": None,
        "cuisine_preference": None,
    }
    result = search_recipes(state)
    recipes = result["matched_recipes"]
    for r in recipes:
        assert "vegan" in r["dietary"]
        assert "gluten-free" in r["dietary"]


def test_search_recipes_no_ingredients():
    state: RecipeAgentState = {
        "ingredients": [],
        "dietary_restrictions": ["vegan"],
        "max_cooking_time": 30,
        "cuisine_preference": None,
    }
    result = search_recipes(state)
    recipes = result["matched_recipes"]
    for r in recipes:
        assert "vegan" in r["dietary"]
        assert r["cooking_time"] <= 30


def test_search_recipes_all_filters():
    state: RecipeAgentState = {
        "ingredients": ["chicken", "rice"],
        "dietary_restrictions": ["gluten-free"],
        "max_cooking_time": 25,
        "cuisine_preference": "Asian",
    }
    result = search_recipes(state)
    recipes = result["matched_recipes"]
    for r in recipes:
        assert r["cooking_time"] <= 25
        assert "gluten-free" in r["dietary"]
        r_ings = set(x.lower() for x in r["ingredients"])
        user_ings = set(x.lower() for x in state["ingredients"])
        assert len(user_ings.intersection(r_ings)) > 0
    # Check scoring
    for r in recipes:
        expected_score = len(user_ings.intersection(set(x.lower() for x in r["ingredients"]))) + (2 if r["cuisine"].lower() == "asian" else 0)
        assert r["score"] == expected_score