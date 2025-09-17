from fastapi import FastAPI
from research_agent.app.routes import router as agents_router

app = FastAPI(
    title="AI Agents API",
    version="0.1.0",
    description="Exposes AI research agent via FastAPI",
)


# include routes
app.include_router(agents_router)


# health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}
