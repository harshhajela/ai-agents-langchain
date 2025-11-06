from typing import Dict, Any, Optional
from research_agent.app.deps import logger, fallback_models
from research_agent.core.components import SearchTool, Summarizer, ResponseParser


def run_research(
    query: str, *, model_name: Optional[str] = None, temperature: Optional[float] = None
) -> Dict[str, Any]:
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
        summarizer = Summarizer(model_name=model_name, temperature=temperature)
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

    # Summarize (with fallback if initial attempt fails)
    prompt_text = summarizer.build_prompt(query, top_results)
    try:
        content = summarizer.summarize(prompt_text)
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        # Try fallbacks
        tried: list[str] = []
        primary_model = getattr(summarizer, "_model_name", None)
        for alt_model in fallback_models(exclude_provider_id=primary_model):
            tried.append(alt_model)
            logger.info(f"Attempting fallback model: {alt_model}")
            try:
                alt = Summarizer(model_name=alt_model, temperature=temperature)
                content = alt.summarize(prompt_text)
                summarizer = alt  # switch to the working summarizer for downstream
                break
            except Exception as ex:
                logger.error(f"Fallback model failed: {alt_model} error={ex}")
                content = None  # ensure not using stale content
        if not content:
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
