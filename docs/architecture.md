# RAG Knowledge Agent — Architecture

## System Overview
A production-quality RAG-powered AI agent exposing a conversational
API via FastAPI. Built with LangGraph orchestration, Chroma vector
storage, and OpenAI gpt-5.4-mini.

## Components

### API Layer (api/main.py)
FastAPI server with three endpoints:
- POST /chat — accepts message + session_id, returns agent response
- DELETE /session/{id} — clears conversation history
- GET /sessions — lists active sessions

### Agent Layer (src/capstone_agent.py)
LangGraph StateGraph with two nodes:
- agent_node — LLM reasoning, tool selection
- tool_node — tool execution, result appending
Conditional edges route between nodes until no tool calls remain.
Hard limit: 6 tool calls per turn to prevent infinite loops.

### Memory Layer
In-memory session store (dict) keyed by session_id.
Each session holds the full LangChain message history.
Conversation context persists across API calls within a session.

### Tools (5)
1. search_knowledge_base — enhanced RAG (hybrid retrieval + reranking)
2. lookup_customer — JSON customer database
3. calculate_pricing — plan/seat/billing pricing engine
4. draft_customer_email — LLM-generated professional emails
5. create_escalation_ticket — ticket creation with SLA assignment

### RAG Pipeline (src/enhanced_rag.py)
Query transformation → hybrid retrieval (vector + BM25) →
LLM reranking → generation with source citation

### Vector Store
Chroma persistent store with text-embedding-3-small embeddings.
50 TechFlow documents across 4 categories:
product_faq, company_policy, support_article, pricing_info.

## Data Flow
User message → FastAPI → session history loaded → LangGraph agent →
tool calls (0–6) → final LLM response → session history saved →
response returned to caller

## Production Considerations
- Replace in-memory session store with Redis or Supabase
- Add authentication to /chat endpoint
- Add human-in-the-loop approval gate for create_escalation_ticket
- Add LangSmith tracing for observability
- Implement rate limiting per session_id