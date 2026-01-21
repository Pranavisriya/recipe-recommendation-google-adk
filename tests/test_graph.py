import pytest
from unittest.mock import Mock
from langchain_core.messages import HumanMessage

from src.recipe_agent.graph import build_recipe_graph


@pytest.fixture
def mock_llm():
    llm = Mock()
    # Mock for extract
    extractor = Mock()
    extractor.invoke.return_value = Mock(
        ingredients=["rice", "vegetables"],
        dietary_restrictions=[],
        max_cooking_time=20,
        cuisine_preference=None
    )
    llm.with_structured_output.return_value = extractor

    # Mock for rank
    llm.invoke.side_effect = [
        Mock(content="Veggie Rice Bowl, Vegetable Fried Rice"),  # rank response
        Mock(content="Based on your ingredients...")  # recommend response
    ]
    return llm


def test_build_recipe_graph(mock_llm, monkeypatch):
    # Mock get_llm to return our mock
    monkeypatch.setattr("src.recipe_agent.graph.get_llm", lambda: mock_llm)

    graph = build_recipe_graph()

    # Test the graph structure
    assert graph is not None

    # Test a simple invocation
    initial_state = {
        "messages": [HumanMessage(content="I have rice and vegetables, 20 minutes.")]
    }

    result = graph.invoke(initial_state)

    assert "messages" in result
    assert len(result["messages"]) > 1  # Should have added responses