import pytest
from unittest.mock import Mock
from langchain_core.messages import AIMessage

from src.recipe_agent.nodes.rank_recipes import rank_recipes_factory
from src.recipe_agent.state import RecipeAgentState


@pytest.fixture
def mock_llm():
    llm = Mock()
    llm.invoke.return_value = AIMessage(content="Veggie Rice Bowl, Vegetable Fried Rice, Mediterranean Rice Salad")
    return llm


def test_rank_recipes_basic(mock_llm):
    rank_func = rank_recipes_factory(mock_llm)

    state: RecipeAgentState = {
        "ingredients": ["rice", "vegetables", "beans", "avocado"],
        "dietary_restrictions": [],
        "max_cooking_time": 20,
        "cuisine_preference": None,
        "matched_recipes": [
            {"name": "Veggie Rice Bowl", "cuisine": "Fusion", "cooking_time": 18, "score": 4},
            {"name": "Vegetable Fried Rice", "cuisine": "Asian", "cooking_time": 15, "score": 3},
            {"name": "Mediterranean Rice Salad", "cuisine": "Mediterranean", "cooking_time": 20, "score": 2},
        ]
    }

    result = rank_func(state)

    ranked = result["matched_recipes"]
    assert len(ranked) == 3
    assert ranked[0]["name"] == "Veggie Rice Bowl"
    assert ranked[1]["name"] == "Vegetable Fried Rice"
    assert ranked[2]["name"] == "Mediterranean Rice Salad"

    # Check LLM was called
    mock_llm.invoke.assert_called_once()


def test_rank_recipes_empty(mock_llm):
    rank_func = rank_recipes_factory(mock_llm)

    state: RecipeAgentState = {
        "matched_recipes": []
    }

    result = rank_func(state)
    assert result["matched_recipes"] == []

    # LLM not called
    mock_llm.invoke.assert_not_called()


def test_rank_recipes_partial_rank(mock_llm):
    mock_llm.invoke.return_value = AIMessage(content="Veggie Rice Bowl")

    rank_func = rank_recipes_factory(mock_llm)

    state: RecipeAgentState = {
        "matched_recipes": [
            {"name": "Veggie Rice Bowl", "cuisine": "Fusion", "cooking_time": 18, "score": 4},
            {"name": "Vegetable Fried Rice", "cuisine": "Asian", "cooking_time": 15, "score": 3},
        ]
    }

    result = rank_func(state)

    ranked = result["matched_recipes"]
    assert len(ranked) == 2
    assert ranked[0]["name"] == "Veggie Rice Bowl"
    assert ranked[1]["name"] == "Vegetable Fried Rice"  # sorted by score


def test_rank_recipes_invalid_names(mock_llm):
    mock_llm.invoke.return_value = AIMessage(content="Invalid Name, Another Invalid")

    rank_func = rank_recipes_factory(mock_llm)

    state: RecipeAgentState = {
        "matched_recipes": [
            {"name": "Veggie Rice Bowl", "cuisine": "Fusion", "cooking_time": 18, "score": 4},
            {"name": "Vegetable Fried Rice", "cuisine": "Asian", "cooking_time": 15, "score": 3},
        ]
    }

    result = rank_func(state)

    ranked = result["matched_recipes"]
    assert len(ranked) == 2
    # Should fall back to score sorting
    assert ranked[0]["name"] == "Veggie Rice Bowl"
    assert ranked[1]["name"] == "Vegetable Fried Rice"