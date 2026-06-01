import json
import math
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

load_dotenv()

# ── STATE ──────────────────────────────────────────────────────────────────────
# State is the shared memory that flows through every node in the graph.
# Every node reads from state and writes back to state.
# add_messages is a reducer — it appends new messages rather than replacing them,
# which is how conversation history accumulates.

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    tool_call_count: int          # tracks how many tool calls have been made
    requires_approval: bool       # flag for human-in-the-loop
    pending_action: str           # stores the action waiting for approval


# ── TOOLS ──────────────────────────────────────────────────────────────────────
# Tools are plain Python functions decorated with @tool.
# LangGraph passes them to the LLM as function schemas.
# The LLM decides when to call them and with what arguments.

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the TechFlow knowledge base for information about products,
    policies, pricing, and support. Use this for any question about
    TechFlow's features, plans, or procedures.
    """
    # Import here to avoid circular imports
    from src.langchain_rag import load_vectorstore, build_rag_chain, ask_langchain
    try:
        vectorstore = load_vectorstore()
        chain, _ = build_rag_chain(vectorstore)
        result = ask_langchain(query, chain)
        return result["answer"]
    except Exception as e:
        return f"Knowledge base search failed: {str(e)}"


@tool
def lookup_customer(customer_id: str) -> str:
    """
    Look up a customer record by their customer ID.
    Returns account details including plan, join date, and status.
    Use this when the user references a specific customer or account.
    """
    # Simulated customer database
    customers = {
        "C001": {"name": "Alice Chen", "plan": "Business", "status": "active",
                 "joined": "2024-03-15", "seats": 12, "storage_used_gb": 47},
        "C002": {"name": "Bob Martinez", "plan": "Pro", "status": "active",
                 "joined": "2023-11-02", "seats": 3, "storage_used_gb": 12},
        "C003": {"name": "Carol White", "plan": "Starter", "status": "suspended",
                 "joined": "2024-07-20", "seats": 2, "storage_used_gb": 0.8},
        "C004": {"name": "David Kim", "plan": "Enterprise", "status": "active",
                 "joined": "2022-05-10", "seats": 150, "storage_used_gb": 890},
    }
    record = customers.get(customer_id.upper())
    if record:
        return json.dumps(record)
    return f"No customer found with ID {customer_id}."


@tool
def calculate_price(plan: str, seats: int, billing: str = "monthly") -> str:
    """
    Calculate the total price for a TechFlow subscription.
    Args:
        plan: One of 'starter', 'pro', 'business', 'enterprise'
        seats: Number of user seats
        billing: 'monthly' or 'annual'
    Returns pricing breakdown as a string.
    """
    pricing = {
        "starter": {"monthly": 0, "annual": 0},
        "pro": {"monthly": 15, "annual": 12},
        "business": {"monthly": 28, "annual": 22},
        "enterprise": {"monthly": None, "annual": None},
    }
    plan_lower = plan.lower()
    if plan_lower not in pricing:
        return f"Unknown plan: {plan}. Valid plans: starter, pro, business, enterprise."
    if plan_lower == "enterprise":
        return "Enterprise pricing is custom. Contact sales@techflow.io for a quote."
    rate = pricing[plan_lower][billing.lower()]
    total = rate * seats
    savings = (pricing[plan_lower]["monthly"] - pricing[plan_lower]["annual"]) * seats * 12
    result = (
        f"Plan: {plan.title()} | Seats: {seats} | Billing: {billing.title()}\n"
        f"Rate: ${rate}/user/month\n"
        f"Total: ${total}/month"
    )
    if billing.lower() == "annual":
        result += f"\nAnnual savings vs monthly: ${savings}"
    return result


@tool
def escalate_issue(customer_id: str, issue_summary: str, priority: str) -> str:
    """
    Escalate a complex issue to the human support team.
    Use this when the issue cannot be resolved with available information,
    requires account changes, or involves billing disputes.
    Args:
        customer_id: The customer's ID
        issue_summary: Brief description of the issue
        priority: 'high', 'medium', or 'low'
    Returns a ticket confirmation.
    """
    ticket_id = f"TKT-{hash(customer_id + issue_summary) % 10000:04d}"
    return (
        f"Escalation ticket created.\n"
        f"Ticket ID: {ticket_id}\n"
        f"Customer: {customer_id}\n"
        f"Priority: {priority.upper()}\n"
        f"Summary: {issue_summary}\n"
        f"A support specialist will follow up within "
        f"{'1 hour' if priority == 'high' else '4 hours' if priority == 'medium' else '24 hours'}."
    )


TOOLS = [search_knowledge_base, lookup_customer, calculate_price, escalate_issue]
TOOL_MAP = {t.name: t for t in TOOLS}

# ── LLM ────────────────────────────────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = """You are a TechFlow support agent with access to tools.

Available tools:
- search_knowledge_base: answer questions about TechFlow products, policies, pricing, support
- lookup_customer: retrieve account details for a specific customer ID
- calculate_price: calculate subscription costs for any plan and seat count
- escalate_issue: create a support ticket for issues requiring human intervention

Guidelines:
- Always use search_knowledge_base before answering product or policy questions
- Use lookup_customer whenever a customer ID is mentioned
- Use calculate_price for any pricing calculation request
- Escalate if the issue involves account suspension, billing disputes, or data loss
- Be concise and helpful
"""


# ── NODES ──────────────────────────────────────────────────────────────────────
# Nodes are functions that receive state, do work, and return state updates.

def agent_node(state: AgentState) -> dict:
    """
    The reasoning node. The LLM reads all messages in state
    and decides: respond directly, or call a tool?
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def tool_node(state: AgentState) -> dict:
    """
    The execution node. Runs whatever tool the LLM requested
    and appends the result as a ToolMessage.
    """
    last_message = state["messages"][-1]
    tool_results = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Check if this tool requires human approval
        if tool_name == "escalate_issue":
            # Set approval flag instead of executing immediately
            return {
                "requires_approval": True,
                "pending_action": f"escalate_issue({tool_args})",
                "messages": []
            }

        tool_fn = TOOL_MAP.get(tool_name)
        if tool_fn:
            result = tool_fn.invoke(tool_args)
        else:
            result = f"Tool '{tool_name}' not found."

        tool_results.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )

    return {
        "messages": tool_results,
        "tool_call_count": state.get("tool_call_count", 0) + 1
    }


def approval_node(state: AgentState) -> dict:
    """
    Human-in-the-loop node. Pauses execution and prompts for approval
    before running high-stakes actions like escalation.
    """
    print(f"\n⚠️  APPROVAL REQUIRED")
    print(f"Pending action: {state['pending_action']}")
    response = input("Approve? (yes/no): ").strip().lower()

    if response == "yes":
        # Execute the pending escalation
        import ast
        # Parse the pending action string back into a function call
        action_str = state["pending_action"]
        args_str = action_str[len("escalate_issue("):-1]
        args = ast.literal_eval(args_str)

        result = escalate_issue.invoke(args)
        # Find the original tool_call_id from the last AI message
        last_ai_msg = next(
            (m for m in reversed(state["messages"]) if hasattr(m, "tool_calls")),
            None
        )
        tool_call_id = last_ai_msg.tool_calls[0]["id"] if last_ai_msg else "unknown"

        return {
            "requires_approval": False,
            "pending_action": "",
            "messages": [ToolMessage(content=result, tool_call_id=tool_call_id)]
        }
    else:
        last_ai_msg = next(
            (m for m in reversed(state["messages"]) if hasattr(m, "tool_calls")),
            None
        )
        tool_call_id = last_ai_msg.tool_calls[0]["id"] if last_ai_msg else "unknown"

        return {
            "requires_approval": False,
            "pending_action": "",
            "messages": [ToolMessage(
                content="Action cancelled by operator.",
                tool_call_id=tool_call_id
            )]
        }


# ── ROUTING ────────────────────────────────────────────────────────────────────
# Conditional edges decide which node to visit next.
# They inspect state and return the name of the next node.

def route_after_agent(state: AgentState) -> str:
    """After the agent reasons, where do we go?"""
    last_message = state["messages"][-1]

    # If the LLM made a tool call, go to tool_node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_node"

    # Otherwise the LLM produced a final answer — end the graph
    return END


def route_after_tool(state: AgentState) -> str:
    """After a tool runs, where do we go?"""

    # Safety valve: stop after 5 tool calls to prevent infinite loops
    if state.get("tool_call_count", 0) >= 5:
        return END

    # If escalation is waiting for approval, go to approval node
    if state.get("requires_approval", False):
        return "approval_node"

    # Otherwise go back to the agent to reason about the tool result
    return "agent_node"


def route_after_approval(state: AgentState) -> str:
    """After approval decision, go back to agent to generate final response."""
    return "agent_node"


# ── GRAPH ──────────────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("agent_node", agent_node)
    graph.add_node("tool_node", tool_node)
    graph.add_node("approval_node", approval_node)

    # Set entry point
    graph.set_entry_point("agent_node")

    # Add conditional edges
    graph.add_conditional_edges("agent_node", route_after_agent)
    graph.add_conditional_edges("tool_node", route_after_tool)
    graph.add_conditional_edges("approval_node", route_after_approval)

    return graph.compile()


# Build once at module level
agent = build_graph()


def run_agent(user_input: str, thread_id: str = "default") -> str:
    """Run the agent on a single user input and return the final response."""
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "tool_call_count": 0,
        "requires_approval": False,
        "pending_action": ""
    }
    final_state = agent.invoke(initial_state)
    last_message = final_state["messages"][-1]
    return last_message.content