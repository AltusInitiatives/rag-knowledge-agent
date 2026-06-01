# RAG Knowledge Agent

A production-quality RAG-powered AI support agent built with LangGraph,
LangChain, and FastAPI. Demonstrates the full Week 7 AI automation stack.

## Architecture
- **Orchestration:** LangGraph StateGraph with conditional routing
- **Retrieval:** Hybrid search (vector + BM25) with LLM reranking
- **Memory:** Per-session conversation history across API calls
- **API:** FastAPI with Pydantic-validated endpoints
- **Vector DB:** Chroma with OpenAI text-embedding-3-small

## Tools
| Tool | Purpose |
|------|---------|
| search_knowledge_base | Enhanced RAG over TechFlow docs |
| lookup_customer | Customer account retrieval |
| calculate_pricing | Plan/seat/billing cost calculator |
| draft_customer_email | LLM-generated email drafts |
| create_escalation_ticket | Support ticket creation with SLA |

## Setup
```bash
uv sync
cp .env.example .env  # add your OPENAI_API_KEY
uv run python scripts/ingest.py
uv run uvicorn api.main:app --reload --port 8000
```

## Usage
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the Business plan price?", "session_id": "demo"}'
```

## Portfolio Context
Built as Week 7 capstone of a 90-day AI Automation Specialist program.
Combines RAG systems (Days 43–45), LangChain (Day 46), LangGraph agents
(Day 47), and CrewAI multi-agent patterns (Day 48).