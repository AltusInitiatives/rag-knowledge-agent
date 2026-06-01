import json
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

load_dotenv()

# ── STATE ──────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    tool_call_count: int


# ── SESSION MEMORY ─────────────────────────────────────────────────────────────
# In-memory store keyed by session_id.
# Persists conversation history across multiple API calls in the same session.
# Resets on server restart — use Redis or Supabase for production persistence.

sessions: dict[str, list] = {}


# ── TOOLS ──────────────────────────────────────────────────────────────────────

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the TechFlow knowledge base for accurate information about products,
    pricing, company policies, and support procedures.
    Use this as the FIRST tool for any question about TechFlow.
    """
    from src.enhanced_rag import ask_enhanced
    try:
        result = ask_enhanced(
            query=query,
            use_query_transform=True,
            use_reranking=True,
            n_retrieve=6,
            n_rerank=3
        )
        return result["answer"]
    except Exception as e:
        return f"Knowledge base search failed: {str(e)}"


@tool
def lookup_customer(customer_id: str) -> str:
    """
    Look up a TechFlow customer record by customer ID (format: C001, C002 etc).
    Returns account details: name, plan, status, seats, storage used, join date.
    Use this whenever a customer ID is mentioned or account details are needed.
    """
    customers = {
        "C001": {"name": "Alice Chen", "plan": "Business", "status": "active",
                 "joined": "2024-03-15", "seats": 12, "storage_used_gb": 47,
                 "email": "alice.chen@acmecorp.com"},
        "C002": {"name": "Bob Martinez", "plan": "Pro", "status": "active",
                 "joined": "2023-11-02", "seats": 3, "storage_used_gb": 12,
                 "email": "bob@martinez-design.com"},
        "C003": {"name": "Carol White", "plan": "Starter", "status": "suspended",
                 "joined": "2024-07-20", "seats": 2, "storage_used_gb": 0.8,
                 "email": "carol.white@freelance.io"},
        "C004": {"name": "David Kim", "plan": "Enterprise", "status": "active",
                 "joined": "2022-05-10", "seats": 150, "storage_used_gb": 890,
                 "email": "d.kim@globaltechsolutions.com"},
    }
    record = customers.get(customer_id.upper())
    if record:
        return json.dumps(record, indent=2)
    return f"No customer found with ID '{customer_id}'. Valid IDs: C001–C004."


@tool
def calculate_pricing(plan: str, seats: int, billing: str = "monthly") -> str:
    """
    Calculate TechFlow subscription pricing.
    Args:
        plan: 'starter', 'pro', 'business', or 'enterprise'
        seats: number of user seats required
        billing: 'monthly' or 'annual'
    Returns a full pricing breakdown including savings for annual billing.
    """
    pricing = {
        "starter":    {"monthly": 0,    "annual": 0},
        "pro":        {"monthly": 15,   "annual": 12},
        "business":   {"monthly": 28,   "annual": 22},
        "enterprise": {"monthly": None, "annual": None},
    }
    plan_key = plan.lower().strip()
    if plan_key not in pricing:
        return f"Unknown plan '{plan}'. Valid plans: starter, pro, business, enterprise."
    if plan_key == "enterprise":
        return "Enterprise pricing is custom. Contact sales@techflow.io for a quote."
    if plan_key == "starter":
        return "The Starter plan is free — up to 5 users, 3 projects, 1GB storage."

    monthly_rate = pricing[plan_key]["monthly"]
    annual_rate  = pricing[plan_key]["annual"]

    if billing.lower() == "annual":
        monthly_total  = monthly_rate * seats
        annual_total   = annual_rate * seats
        annual_savings = (monthly_rate - annual_rate) * seats * 12
        return (
            f"Plan: {plan.title()} | Seats: {seats} | Billing: Annual\n"
            f"Rate: ${annual_rate}/user/month (billed annually)\n"
            f"Monthly equivalent: ${annual_total:,}/month\n"
            f"Annual total: ${annual_total * 12:,}/year\n"
            f"Savings vs monthly billing: ${annual_savings:,}/year"
        )
    else:
        total = monthly_rate * seats
        return (
            f"Plan: {plan.title()} | Seats: {seats} | Billing: Monthly\n"
            f"Rate: ${monthly_rate}/user/month\n"
            f"Monthly total: ${total:,}/month\n"
            f"Tip: Switch to annual billing to save "
            f"${(monthly_rate - annual_rate) * seats * 12:,}/year"
        )


@tool
def draft_customer_email(
    recipient_name: str,
    email_type: str,
    context: str
) -> str:
    """
    Draft a professional customer email for a TechFlow support scenario.
    Args:
        recipient_name: The customer's first name
        email_type: One of 'support_response', 'account_notice',
                    'upgrade_recommendation', 'escalation_confirmation'
        context: Key information to include in the email
                 (issue details, resolution, next steps, etc.)
    Returns a complete, ready-to-send email draft.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    prompt = f"""Draft a professional, warm customer email for TechFlow support.

Recipient first name: {recipient_name}
Email type: {email_type}
Context to include: {context}

Guidelines:
- Subject line on the first line, format: Subject: [subject]
- Blank line after subject
- Professional but approachable tone
- Under 150 words
- Sign off as: TechFlow Support Team
- Do not add placeholders like [Your Name] or [Date]"""

    response = llm.invoke(prompt)
    return response.content


@tool
def create_escalation_ticket(
    customer_id: str,
    issue_summary: str,
    priority: str,
    category: str = "general"
) -> str:
    """
    Create an escalation ticket for issues requiring human specialist intervention.
    Use this for: account suspensions, billing disputes, data loss, security concerns,
    or any issue that cannot be resolved with available information.
    Args:
        customer_id: Customer ID (e.g. C001)
        issue_summary: Clear description of the issue
        priority: 'high', 'medium', or 'low'
        category: 'billing', 'technical', 'account', 'security', or 'general'
    """
    ticket_id = f"TKT-{abs(hash(customer_id + issue_summary)) % 9000 + 1000}"
    sla = {"high": "1 hour", "medium": "4 hours", "low": "24 hours"}
    response_time = sla.get(priority.lower(), "24 hours")
    return (
        f"✅ Escalation ticket created successfully.\n"
        f"Ticket ID:      {ticket_id}\n"
        f"Customer:       {customer_id}\n"
        f"Category:       {category.title()}\n"
        f"Priority:       {priority.upper()}\n"
        f"Response SLA:   {response_time}\n"
        f"Summary:        {issue_summary}\n\n"
        f"A specialist will follow up with the customer within {response_time}."
    )


TOOLS = [
    search_knowledge_base,
    lookup_customer,
    calculate_pricing,
    draft_customer_email,
    create_escalation_ticket,
]
TOOL_MAP = {t.name: t for t in TOOLS}

# ── LLM ────────────────────────────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = """You are a knowledgeable TechFlow support agent. You help customers
and internal staff with product questions, account management, pricing, and issue resolution.

Tools available to you:
- search_knowledge_base: ALWAYS use this first for any TechFlow product, policy, or support question
- lookup_customer: use when a customer ID is mentioned or account details are needed
- calculate_pricing: use for any pricing or cost calculation request
- draft_customer_email: use when asked to write or draft an email to a customer
- create_escalation_ticket: use for issues requiring human intervention

Guidelines:
- Use search_knowledge_base before answering any product or policy question
- Combine tools when a query requires multiple pieces of information
- Be concise, accurate, and helpful
- If information is not in the knowledge base, say so — do not invent details
- For sensitive actions (suspensions, billing disputes), create an escalation ticket
- When a query requires both customer data AND pricing, call lookup_customer
  first, then ALWAYS follow up with calculate_pricing using the plan and
  seats from the customer record — do not stop after the first tool call"""


# ── NODES ──────────────────────────────────────────────────────────────────────

def agent_node(state: AgentState) -> dict:
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def tool_node(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    results = []
    for tool_call in last_message.tool_calls:
        fn = TOOL_MAP.get(tool_call["name"])
        if fn:
            try:
                result = fn.invoke(tool_call["args"])
            except Exception as e:
                result = f"Tool error: {str(e)}"
        else:
            result = f"Unknown tool: {tool_call['name']}"
        results.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )
    return {
        "messages": results,
        "tool_call_count": state.get("tool_call_count", 0) + 1
    }


# ── ROUTING ────────────────────────────────────────────────────────────────────

def route_after_agent(state: AgentState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tool_node"
    return END


def route_after_tool(state: AgentState) -> str:
    if state.get("tool_call_count", 0) >= 6:
        return END
    return "agent_node"


# ── GRAPH ──────────────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent_node", agent_node)
    graph.add_node("tool_node", tool_node)
    graph.set_entry_point("agent_node")
    graph.add_conditional_edges("agent_node", route_after_agent)
    graph.add_conditional_edges("tool_node", route_after_tool)
    return graph.compile()


agent = build_graph()


# ── PUBLIC INTERFACE ───────────────────────────────────────────────────────────

def chat(message: str, session_id: str = "default") -> str:
    """
    Send a message to the agent and get a response.
    Conversation history is maintained per session_id.
    """
    history = sessions.get(session_id, [])

    initial_state = {
        "messages": history + [HumanMessage(content=message)],
        "tool_call_count": 0
    }

    final_state = agent.invoke(initial_state)
    sessions[session_id] = final_state["messages"]

    return final_state["messages"][-1].content


def clear_session(session_id: str) -> bool:
    """Clear conversation history for a session."""
    if session_id in sessions:
        del sessions[session_id]
        return True
    return False


def list_sessions() -> list[str]:
    """Return all active session IDs."""
    return list(sessions.keys())