from unittest.mock import patch
from research_agent.core.research import run_research


@patch("research_agent.core.research.TavilySearch")
@patch("research_agent.core.research.ChatOpenAI")
def test_run_research_success(mock_llm, mock_tavily):
    # Mock Tavily response
    mock_tavily.return_value.invoke.return_value = {
        "results": [
            {"url": "http://example.com", "title": "Example", "content": "Some content"}
        ]
    }
    # Mock LLM response
    mock_llm.return_value.invoke.return_value = type(
        "obj",
        (),
        {
            "content": "# Summary\nMock summary\n\n# Sources\n- [Example]"
            + "(http://example.com)"
        },
    )

    result = run_research("test query")
    assert "query" in result
    assert "final_summary" in result
    assert "sources" in result
    assert result["sources"][0]["title"] == "Example"


@patch("research_agent.core.research.TavilySearch")
def test_run_research_tavily_failure(mock_tavily):
    mock_tavily.return_value.invoke.side_effect = Exception("Tavily down")

    result = run_research("test query")
    assert "Error" in result["final_summary"]
    assert result["sources"] == []
