# LangGraph Agent Test Results

## 1. Tool Routing
[Table: query → tool called → correct? for all 15 queries]
Every query hit the right tool. Knowledge base queries (Q1–Q3, Q12–Q13, Q15) went through search_knowledge_base. Customer lookups (Q4–Q5) hit lookup_customer. Pricing queries (Q6–Q7, Q11, Q14) hit calculate_price. No misroutes.

## 2. Multi-Tool Chaining (Q8)
[What happened step by step. What two tools were called and in what order.
What the final answer was and whether the math was correct.]
The agent correctly chained two tools without you telling it to. It called lookup_customer("C001") first, got Alice Chen's Business plan with 12 seats, then called calculate_price("business", 12, "annual"), computed the savings, and synthesized a coherent answer. The math is correct: 12 seats × ($28 - $22) × 12 months = $864 saved annually. This is the agent loop working exactly as designed — tool result appended to state, LLM reads it, decides another tool call is needed, executes it, then generates the final answer.

## 3. Edge Cases
[Q10 (C999) — what the agent returned and why it's correct behavior]
[Q11 (Enterprise) — what the agent returned and why it's correct behavior]
C999 returned a graceful "no customer found" message — the tool returned the error string and the agent relayed it cleanly. Enterprise pricing correctly deflected to sales contact rather than attempting to calculate a number that doesn't exist in the pricing table.

## 4. Human-in-the-Loop (Q9)
[Describe the approval flow — what printed, what you typed, what happened after]
The graph paused at the approval node, printed the pending action with full arguments, waited for your input, and only executed the escalation after you typed yes. Ticket TKT-2033 was created with high priority and the correct 1-hour SLA. This is the pattern you'll use in client projects for any irreversible action — sending emails, making API calls that cost money, modifying production data.

## 5. Knowledge Gap Handling (Q13)
[What the agent said and why this is correct behavior vs hallucination]
The agent correctly said the knowledge base doesn't have step-by-step Okta setup instructions and recommended checking TechFlow docs. This is correct behavior. The knowledge base has the SSO policy (which plans support it, which providers) but not the setup procedure. The agent didn't hallucinate steps — it acknowledged the gap and redirected. Good prompt discipline.

## 6. Issues
- Deprecation warning on Chroma import — fix: uv add langchain-chroma,
  update import in langchain_rag.py
- EDIT: Updated in project folder.