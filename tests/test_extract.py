from __future__ import annotations

from unittest.mock import Mock

import pytest
from langchain_core.messages import HumanMessage

from src.recipe_agent.nodes.extract_user_preferences import extract_user_preferences_factory
from src.recipe_agent.schemas import UserInput
from src.recipe_agent.state import RecipeAgentState


@pytest.fixture()
def mock_llm():
    llm = Mock()
    extractor = Mock()
    extractor.invoke.return_value = UserInput(
        ingredients=["rice", "vegetables", "beans"],
        dietary_restrictions=["vegan"],
        max_cooking_time=20,
        cuisine_preference="Asian",
    )
    llm.with_structured_output.return_value = extractor
    return llm


def test_extract_user_preferences_basic(mock_llm):
    extract_func = extract_user_preferences_factory(mock_llm)

    state: RecipeAgentState = {
        "messages": [HumanMessage(content="I have rice, vegetables, beans and 20 minutes.")],
    }

    result = extract_func(state)

    assert result["ingredients"] == ["rice", "vegetables", "beans"]
    assert result["dietary_restrictions"] == ["vegan"]
    assert result["max_cooking_time"] == 20
    assert result["cuisine_preference"] == "Asian"

    extractor = mock_llm.with_structured_output.return_value
    extractor.invoke.assert_called_once()
    call_args = extractor.invoke.call_args[0][0]
    assert len(call_args) == 2  # system + user message
    assert call_args[0]["role"] == "system"
    assert "You extract structured cooking preferences" in call_args[0]["content"]
    assert call_args[1] == HumanMessage(content="I have rice, vegetables, beans and 20 minutes.")


def test_extract_user_preferences_empty(mock_llm):
    extract_func = extract_user_preferences_factory(mock_llm)
    extractor = mock_llm.with_structured_output.return_value
    extractor.invoke.return_value = UserInput(
        ingredients=[],
        dietary_restrictions=[],
        max_cooking_time=None,
        cuisine_preference=None,
    )

    state: RecipeAgentState = {"messages": [HumanMessage(content="")]}
    result = extract_func(state)

    assert result["ingredients"] == []
    assert result["dietary_restrictions"] == []
    assert result["max_cooking_time"] is None
    assert result["cuisine_preference"] is None