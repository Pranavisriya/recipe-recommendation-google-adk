import pytest
from unittest.mock import Mock
from langchain_core.messages import AIMessage

from src.recipe_agent.nodes.generate_recommendation import generate_recommendation_factory
from src.recipe_agent.state import RecipeAgentState


@pytest.fixture
def mock_llm():
    llm = Mock()
    llm.invoke.return_value = AIMessage(content="Based on your ingredients and preferences, here are 3 recipes:\n1. Veggie Rice Bowl (18 min) - Fusion\n2. Vegetable Fried Rice (15 min) - Asian\n3. Mediterranean Rice Salad (20 min) - Mediterranean\nWhich one would you like the full recipe for?")
    return llm


def test_generate_recommendation(mock_llm):
    recommend_func = generate_recommendation_factory(mock_llm)

    state: RecipeAgentState = {
        "ingredients": ["rice", "vegetables", "beans", "avocado"],
        "matched_recipes": [
            {"name": "Veggie Rice Bowl", "cooking_time": 18, "cuisine": "Fusion"},
            {"name": "Vegetable Fried Rice", "cooking_time": 15, "cuisine": "Asian"},
            {"name": "Mediterranean Rice Salad", "cooking_time": 20, "cuisine": "Mediterranean"},
        ]
    }

    result = recommend_func(state)

    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert "Veggie Rice Bowl" in result["messages"][0].content
    assert "Which one would you like the full recipe for?" in result["messages"][0].content

    mock_llm.invoke.assert_called_once()


def test_generate_recommendation_no_ingredients(mock_llm):
    recommend_func = generate_recommendation_factory(mock_llm)

    state: RecipeAgentState = {
        "ingredients": [],
        "matched_recipes": []
    }

    result = recommend_func(state)

    assert result["messages"][0].content == "Tell me what ingredients you have so I can recommend recipes."

    mock_llm.invoke.assert_not_called()


def test_generate_recommendation_no_recipes(mock_llm):
    recommend_func = generate_recommendation_factory(mock_llm)

    state: RecipeAgentState = {
        "ingredients": ["rice"],
        "matched_recipes": []
    }

    result = recommend_func(state)

    assert "I couldn’t find a matching recipe" in result["messages"][0].content

    mock_llm.invoke.assert_not_called()