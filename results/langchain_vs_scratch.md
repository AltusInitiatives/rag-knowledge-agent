# LangChain vs From-Scratch RAG — Comparison Analysis

## 1. Code Complexity

| Component | Scratch Version | LangChain Version |
|-----------|----------------|-------------------|
| Files required | embedder.py, vector_store.py, chunker.py, rag.py (4 files) | langchain_rag.py (1 file) |
| Total lines | 19 + 40 + 33 + 66 = 158 | 125 |
| Key difference | Scratch Version: As name suggests, had to build everything from scratch. | LangChain Version: Uses a variety of built-in tools for easier building sequence. |

**Summary:** The scratch version is actually more readable for someone learning — every step is explicit and visible. The real tradeoff is readability for experienced developers vs educational transparency. LangChain is faster to read if you know the framework; scratch is easier to understand if you don't.

---

## 2. Answer Quality

| Question | Scratch | LangChain | Winner |
|----------|---------|-----------|--------|
| Q1 (Slack connection) | Partial refusal | Correct answer | LangChain |
| Q19 (Startup program) | Missing apply details | Included apply details | LangChain |
| All others (18/20) | Equivalent | Equivalent | Tie |

**Root cause of LangChain wins:** LangChain’s text splitters produce higher-quality results because they avoid "blind" character slicing in favor of context-aware, hierarchical chunking. This ensures text breaks at natural semantic boundaries (like paragraphs and sentences) rather than mid-word, preserving the meaning required for accurate AI responses.

**Overall:** LangChain is better overall with the reason being that edge cases are covered as well.

---

## 3. LCEL Chain — Structured Output

**All 5 inputs returned valid structured JSON:** ✅

| Input | Category | Priority | Sentiment | Correct? |
|-------|----------|----------|-----------|----------|
| Can't log in, presentation in 20 min | bug | high | negative | ✅ |
| Love the new dashboard update | compliment | low | positive | ✅ |
| How do I export data to CSV? | question | medium | neutral | ✅ |
| API returning 429 errors under limit | bug | high | negative | ✅ |
| Add a dark mode option | feature_request | medium | positive | ✅ |

**What breaks without the parser step:** Without the JsonOutputParser, the chain returns a ChatMessage object. You'd have to manually extract .content, then call json.loads() on it yourself — and handle parsing errors manually. The parser automates that entire step.

---

## Key Takeaways

- Use LangChain when building quickly or when the framework's built-in 
  components (splitters, retrievers, chains) cover your use case; use 
  scratch when you need full control over retrieval logic, custom chunking 
  behavior, or components the framework doesn't support.
- LCEL's pipe syntax makes complex multi-step pipelines readable as a single 
  expression, and makes swapping components (e.g. OpenAI → Anthropic) a 
  one-line change instead of a refactor.
- Structured output chains — prompt → LLM → parser → typed dict — are the 
  foundation of every AI automation that feeds model output into downstream 
  systems like databases, APIs, or no-code platforms.