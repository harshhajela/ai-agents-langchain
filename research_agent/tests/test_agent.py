from unittest.mock import patch
from research_agent.core.research import run_research


@patch("research_agent.core.components.Summarizer.summarize")
@patch("research_agent.core.components.SearchTool.search")
def test_run_research_success(mock_search, mock_summarize):
    # Mock search results
    mock_search.return_value = (
        [
            type(
                "R",
                (),
                {
                    "title": "Example",
                    "url": "http://example.com",
                    "snippet": "Some content",
                },
            )
        ],
        {},
    )
    # Mock LLM content
    mock_summarize.return_value = (
        "# Summary\nMock summary\n\n# Sources\n- [Example](http://example.com)"
    )

    result = run_research("test query")
    assert result["query"] == "test query"
    assert result["final_summary"].startswith("Mock summary")
    assert result["sources"][0]["title"] == "Example"


@patch("research_agent.core.components.SearchTool.search")
def test_run_research_search_failure(mock_search):
    mock_search.side_effect = Exception("Search down")
    result = run_research("test query")
    assert "Error" in result["final_summary"]
    assert result["sources"] == []


def test_response_parser():
    from research_agent.core.components import ResponseParser

    content = "# Summary\nHello\n\n# Sources\n- [A](http://a.com)\n* http://b.com"
    parsed = ResponseParser.parse_content(content)
    assert parsed["summary_md"].startswith("Hello")
    assert len(parsed["sources"]) == 2
