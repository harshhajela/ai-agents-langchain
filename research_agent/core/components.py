from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from research_agent.app.deps import settings


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


class SearchTool:
    def __init__(self) -> None:
        # Lazy init to make unit testing easier without real keys
        self._tool: TavilySearch | None = None

    def _ensure_tool(self) -> None:
        if self._tool is not None:
            return
        tavily_key = (
            settings.tavily_api_key.get_secret_value()
            if settings.tavily_api_key
            else None
        )
        if tavily_key:
            self._tool = TavilySearch(tavily_api_key=tavily_key)
        else:
            self._tool = TavilySearch()

    def search(
        self, query: str, limit: int = 5
    ) -> Tuple[List[SearchResult], Dict[str, Any]]:
        self._ensure_tool()
        payload = {"query": query}
        raw = self._tool.invoke(payload)  # type: ignore[union-attr]
        results = raw.get("results", [])[:limit]
        parsed = [
            SearchResult(
                title=r.get("title", "No title"),
                url=r.get("url", ""),
                snippet=r.get("snippet", r.get("content", "")),
            )
            for r in results
        ]
        return parsed, raw


class Summarizer:
    def __init__(self) -> None:
        openrouter_key = (
            settings.openrouter_api_key.get_secret_value()
            if settings.openrouter_api_key
            else None
        )
        openai_key = (
            settings.openai_api_key.get_secret_value()
            if settings.openai_api_key
            else None
        )
        if openrouter_key:
            self._llm = ChatOpenAI(
                model=settings.model_name,
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=settings.temperature,
            )
        elif openai_key:
            self._llm = ChatOpenAI(
                model=settings.model_name,
                api_key=openai_key,
                temperature=settings.temperature,
            )
        else:
            self._llm = ChatOpenAI(
                model=settings.model_name, temperature=settings.temperature
            )

    @staticmethod
    def build_context(results: List[SearchResult]) -> str:
        lines: List[str] = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. [{r.title}]({r.url})\n{r.snippet}\n")
        return "\n".join(lines)

    @staticmethod
    def build_prompt(query: str, results: List[SearchResult]) -> str:
        context_text = Summarizer.build_context(results)
        return f"""
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

    def summarize(self, prompt_text: str) -> str:
        # Accept raw prompt text to make unit testing easier
        from langchain_core.messages import HumanMessage

        response = self._llm.invoke([HumanMessage(content=prompt_text)])
        return response.content


class ResponseParser:
    @staticmethod
    def parse_content(content: str) -> Dict[str, Any]:
        # Extract sources
        sources: List[Dict[str, str]] = []
        if "# Sources" in content:
            sources_section = content.split("# Sources", 1)[1]
            for line in sources_section.splitlines():
                s = line.strip()
                if s.startswith("- ") or s.startswith("* "):
                    s = s[2:].strip()
                if s.startswith("[") and "](" in s and s.endswith(")"):
                    try:
                        text = s[s.index("[") + 1 : s.index("]")]
                        url = s[s.index("(") + 1 : s.index(")")]
                        sources.append({"title": text, "url": url})
                    except Exception:
                        continue
                elif s.startswith("http"):
                    sources.append({"title": s, "url": s})

        # Extract summary
        if "# Summary" in content:
            try:
                summary = (
                    content.split("# Summary", 1)[1].split("# Sources", 1)[0].strip()
                )
            except Exception:
                summary = content
        else:
            summary = content.strip()

        return {"summary_md": summary, "sources": sources}
