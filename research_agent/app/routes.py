from fastapi import APIRouter, HTTPException
from research_agent.app.schemas import ResearchPayload, ResearchResponse
from research_agent.core.research import run_research
from research_agent.app.deps import logger

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/research", response_model=ResearchResponse)
def research_endpoint(payload: ResearchPayload):
    try:
        result = run_research(payload.query)
        return ResearchResponse(
            query=result["query"],
            final_summary=result["final_summary"],
            sources=result["sources"],
        )
    except Exception as e:
        logger.error(f"Research agent failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Research agent failed")