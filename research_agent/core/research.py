from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from research_agent.app.deps import settings, logger


# This file contains core research logic.


def run_research(query: str) -> Dict[str, Any]:
    # Initialize TavilySearch tool with API key
    try:
        tavily_tool = TavilySearch(api_key=settings.tavily_api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Tavily Search: {e}")
        return {
            "query": query,
            "final_summary": "Error: Failed to initialize search tool.",
            "sources": [],
        }

    # Initialize ChatOpenAI language model with specified params from settings
    try:
        llm = ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=settings.temperature,
        )
    except Exception as e:
        logger.error(f"Failed to initialize ChatOpenAI: {e}")
        return {
            "query": query,
            "final_summary": "Error: Failed to initialize language model.",
            "sources": [],
        }

    # Call TavilySearch once with the query to retrieve search results
    try:
        tavily_results = tavily_tool.invoke({"query": query})
    except Exception as e:
        logger.error(f"Error during TavilySearch invocation: {e}")
        return {
            "query": query,
            "final_summary": "Error: Search invocation failed.",
            "sources": [],
        }

    # Extract top 5 results from TavilySearch response
    top_results = tavily_results.get("results", [])[:5]

    # Format context text with titles, URLs, and snippets for prompt
    context_lines = []
    for i, res in enumerate(top_results, 1):
        title = res.get("title", "No title")
        url = res.get("url", "")
        snippet = res.get("snippet", "")
        context_lines.append(f"{i}. [{title}]({url})\n{snippet}\n")
    context_text = "\n".join(context_lines)

    # Prepare the prompt text with instructions and context for the LLM
    prompt_text = f"""
You are a meticulous research assistant.

Task: Research the following query:
"{query}"

Context: Here are some relevant search results:
{context_text}

Rules:
- Produce a detailed Markdown summary with sections.
- Do NOT use placeholders.
- Always include at least 3 sources in the 'Sources' section as markdown links.

Format strictly as:

# Summary
<actual summary>

# Sources
- [Title](URL)
- [Title](URL)
- [Title](URL)
"""

    # Invoke the language model with the prepared prompt
    try:
        response = llm.invoke([HumanMessage(content=prompt_text)])
    except Exception as e:
        logger.error(f"Error during LLM invocation: {e}")
        return {
            "query": query,
            "final_summary": "Error: Language model invocation failed.",
            "sources": [],
        }

    # Extract the full content from the LLM response
    final_content = response.content

    # Parse the sources section from the LLM response content
    sources = []
    if "# Sources" in final_content:
        sources_section = final_content.split("# Sources", 1)[1]
        for line in sources_section.splitlines():
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                line = line[2:].strip()
            if line.startswith("[") and "](" in line and line.endswith(")"):
                try:
                    text = line[line.index("[") + 1 : line.index("]")]
                    url = line[line.index("(") + 1 : line.index(")")]
                    sources.append({"title": text, "url": url})
                except Exception:
                    continue
            elif line.startswith("http"):
                sources.append({"title": line, "url": line})

    # Extract the summary markdown from the LLM response content
    summary_md = (
        final_content.split("# Summary", 1)[1].split("# Sources", 1)[0].strip()
        if "# Summary" in final_content
        else final_content.strip()
    )

    # Return a plain dictionary containing the results
    return {
        "query": query,
        "raw_messages": [response],
        "final_summary": summary_md,
        "sources": sources,
    }


if __name__ == "__main__":
    result = run_research("Summarize the latest research on AI agents in healthcare")
    print(result)
