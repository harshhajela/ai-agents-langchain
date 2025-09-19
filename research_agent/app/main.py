import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from research_agent.app.routes import router as agents_router
from research_agent.app.deps import logger
from research_agent import __version__

app = FastAPI(
    title="AI Agents API",
    version=__version__,
    description="Exposes AI research agent via FastAPI",
)

origins = [
    "http://localhost:4200",
    "https://ai-agents.harshhajela.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Simple request timing middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    try:
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            f"request_id={request_id} method={request.method} "
            f"path={request.url.path} status={response.status_code} "
            f"time_ms={duration_ms}"
        )
        response.headers["x-request-id"] = request_id
        return response
    except Exception as e:
        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.error(
            f"request_id={request_id} method={request.method} "
            f"path={request.url.path} error={e} time_ms={duration_ms}"
        )
        raise


# include routes
app.include_router(agents_router)


# health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "version": __version__}
