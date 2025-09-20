from typing import Dict, Any
from research_agent.app.deps import logger
from research_agent.core.components import SearchTool, Summarizer, ResponseParser


def run_research(query: str) -> Dict[str, Any]:
    # Initialize components
    try:
        search = SearchTool()
    except Exception as e:
        logger.error(f"Failed to initialize search tool: {e}")
        return {
            "query": query,
            "final_summary": "Error: Failed to initialize search tool.",
            "sources": [],
        }

    try:
        summarizer = Summarizer()
    except Exception as e:
        logger.error(f"Failed to initialize summarizer: {e}")
        return {
            "query": query,
            "final_summary": "Error: Failed to initialize language model.",
            "sources": [],
        }

    # Search
    try:
        top_results, _raw = search.search(query, limit=5)
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return {
            "query": query,
            "final_summary": "Error: Search invocation failed.",
            "sources": [],
        }

    # Summarize
    try:
        prompt_text = summarizer.build_prompt(query, top_results)
        content = summarizer.summarize(prompt_text)
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        return {
            "query": query,
            "final_summary": "Error: Language model invocation failed.",
            "sources": [],
        }

    # Parse
    parsed = ResponseParser.parse_content(content)
    result = {
        "query": query,
        "final_summary": parsed["summary_md"],
        "sources": parsed["sources"],
    }
    return result
