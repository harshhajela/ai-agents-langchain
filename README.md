# ai-agents-langchain

## Project Overview
ai-agents-langchain is a collection of LangChain-based AI agents designed to assist with various tasks by leveraging state-of-the-art AI technologies. The project aims to provide modular, extensible agents that can be integrated into different workflows to enhance productivity and research capabilities.

## Modules
- `research_agent/`: A research assistant agent powered by LangChain, Tavily, and OpenRouter. It helps users conduct research by automating information retrieval and synthesis.
- *Future Modules*: Additional AI agents will be added here to cover more use cases and domains.

## Tech Stack
- **LangChain**: Framework for building language model applications
- **OpenRouter**: API gateway for language models
- **Tavily**: AI integration platform
- **Python**: Core programming language
- **FastAPI**: Web framework for building APIs
- **Docker**: Containerization platform for deployment

## Getting Started

### Clone the repository
```bash
git clone https://github.com/yourusername/ai-agents-langchain.git
cd ai-agents-langchain
```

### Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run FastAPI locally
```bash
uvicorn research_agent.app.main:app --reload
```
This will start the server at `http://127.0.0.1:8000`.

### Run tests
```bash
pytest
```

## Docker

### Build the Docker image
```bash
docker build -t ai-agents-langchain .
```
Note: A single Docker image is built for the entire project, encompassing all modules.

### Run the Docker container
```bash
docker run -p 8000:8000 ghcr.io/<your-username>/research-agent:1.0.0
```
The API will be accessible at `http://localhost:8000`.

## Versioning
- Single source of truth: `research_agent/__init__.py` contains `__version__`.
- Use Semantic Versioning: bump patch (1.0.1), minor (1.1.0), or major (2.0.0) as appropriate.
- Release process:
  1. Update `__version__` in `research_agent/__init__.py`.
  2. Commit and push to `main`.
  3. CI builds and publishes Docker images:
     - `ghcr.io/<your-username>/research-agent:<version>`
     - `ghcr.io/<your-username>/research-agent:latest`

## CI/CD
- Workflow: `.github/workflows/ci.yml`
- Steps: checkout, install deps, run flake8 + black --check + pytest, build Docker, push to GHCR with version from `research_agent.__version__`.

## Configuration & Secrets
- Use `.env` locally by copying from `.env.example` and filling values.
- Do not commit real secrets. `.env` is already ignored and not copied into Docker images (see `.dockerignore`).
- In CI/CD (GitHub Actions), configure repository Secrets for:
  - `OPENROUTER_API_KEY` (or `OPENAI_API_KEY`)
  - `TAVILY_API_KEY`
  - `MONGODB_URI` (for storing research history)
  - AWS credentials used for deployment (if you build/push from CI)

## CI/CD and Docker (Backend)
- Backend runs as a Docker container on EC2 behind an ALB.
- Provide env vars via your CI/CD secret store and write a runtime `.env` file using `scripts/write-env-file.sh`.
- Build locally: `scripts/build-image.sh` (override `IMAGE_NAME`, `IMAGE_TAG` as needed).
- Run locally: `scripts/run-container.sh` (uses `.env` by default).

Google Sheets persistence:
- Provide `GOOGLE_SERVICE_ACCOUNT_JSON` (full JSON as one string), `GSPREAD_SHEET_ID`, and optional `GSPREAD_WORKSHEET` (defaults to `history`).
- POST `/agents/research` appends a row for successful runs; GET `/agents/research/history?limit=20` reads recent entries.

## Logging
- Writes logs to stdout and to a rotated file at `/var/log/ai-agents/app.log` (created in the container).
- Rotation: daily, keeping last 7 files (configurable via env: `LOG_ROTATION_WHEN`, `LOG_ROTATION_BACKUP_COUNT`).
- Level: INFO by default (`LOG_LEVEL`).
- Each API request logs: `request_id`, `method`, `path`, `status`, `time_ms`.
- To avoid duplicate access logs, you can run uvicorn with `--no-access-log`.
