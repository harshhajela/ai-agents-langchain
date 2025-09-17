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
pip install -r requirements.txt
```

### Run FastAPI locally
```bash
uvicorn main:app --reload
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
docker run -p 8000:8000 ai-agents-langchain
```
The API will be accessible at `http://localhost:8000`.
