from fastapi import APIRouter, HTTPException, BackgroundTasks
from research_agent.app.schemas import (
    ResearchPayload,
    ResearchResponse,
    ResearchHistoryResponse,
    ResearchRecord,
)
from research_agent.core.research import run_research
from research_agent.app.deps import logger
from research_agent.services import sheets


router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/research", response_model=ResearchResponse)
def research_endpoint(payload: ResearchPayload, background_tasks: BackgroundTasks):
    try:
        result = run_research(payload.query)
        # Persist asynchronously after returning response
        if not result["final_summary"].startswith("Error"):
            background_tasks.add_task(sheets.append_research_result, result)
        return ResearchResponse(
            query=result["query"],
            final_summary=result["final_summary"],
            sources=result["sources"],
        )
    except Exception as e:
        logger.error(f"Research agent failed: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error: Research agent failed"
        )


@router.get("/research/history", response_model=ResearchHistoryResponse)
def research_history(limit: int = 20):
    try:
        items = sheets.read_research_history(limit=limit)
        # Coerce into response model list
        return ResearchHistoryResponse(
            items=[
                ResearchRecord(
                    query=i.get("query", ""),
                    final_summary=i.get("final_summary", ""),
                    sources=i.get("sources", []),
                    created_at=i.get("created_at"),
                )
                for i in items
            ]
        )
    except Exception as e:
        logger.error(f"Failed to fetch research history: {e}")
        raise HTTPException(
            status_code=500, detail="Internal Server Error: history failed"
        )
