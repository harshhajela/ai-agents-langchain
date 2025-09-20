from fastapi.testclient import TestClient
from research_agent.app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data.get("version"), str)


def test_research_endpoint_success(monkeypatch):
    def mock_run_research(query: str):
        return {
            "query": query,
            "final_summary": "Mocked summary",
            "sources": [{"title": "Mock Source", "url": "http://example.com"}],
        }

    from research_agent.app import routes
    from research_agent.services import sheets
    from research_agent.app.deps import settings

    calls = {"count": 0}

    def fake_append(data):
        calls["count"] += 1

    monkeypatch.setattr(routes, "run_research", mock_run_research)
    monkeypatch.setattr(sheets, "append_research_result", fake_append)
    # enable persistence for this test only
    monkeypatch.setattr(settings, "persist_results", True, raising=False)

    response = client.post("/agents/research", json={"query": "AI in healthcare"})
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "AI in healthcare"
    assert "Mocked summary" in data["final_summary"]
    assert len(data["sources"]) == 1
    assert calls["count"] == 1


def test_research_endpoint_failure(monkeypatch):
    def mock_run_research(query: str):
        raise Exception("LLM error")

    from research_agent.app import routes

    monkeypatch.setattr(routes, "run_research", mock_run_research)

    response = client.post("/agents/research", json={"query": "AI in finance"})
    assert response.status_code == 500
    assert "Internal Server Error" in response.json()["detail"]
