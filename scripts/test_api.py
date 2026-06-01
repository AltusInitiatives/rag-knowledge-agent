import httpx
import json

BASE_URL = "http://localhost:8000"


def chat(message: str, session_id: str = "default") -> str:
    response = httpx.post(
        f"{BASE_URL}/chat",
        json={"message": message, "session_id": session_id},
        timeout=60
    )
    response.raise_for_status()
    return response.json()["response"]


def clear(session_id: str):
    httpx.delete(f"{BASE_URL}/session/{session_id}")


def section(title: str):
    print(f"\n{'=' * 65}")
    print(f"  {title}")
    print("=" * 65)


def run(label: str, message: str, session_id: str = "default"):
    print(f"\n[{label}] {message}")
    print("-" * 50)
    print(chat(message, session_id))


def main():
    # ── Health check ──────────────────────────────────────────────
    r = httpx.get(f"{BASE_URL}/health")
    print(f"Health: {r.json()}")

    # ── Knowledge base queries ────────────────────────────────────
    section("1. Knowledge Base Queries")
    run("Q1", "What integrations does TechFlow support?", "kb_session")
    run("Q2", "What is the refund policy for annual plans?", "kb_session")
    run("Q3", "How does AI task auto-assignment work?", "kb_session")

    # ── Customer lookup ───────────────────────────────────────────
    section("2. Customer Lookup")
    run("Q4", "Pull up the account for customer C001.", "lookup_session")
    run("Q5", "What plan is customer C003 on, and is there anything unusual?",
        "lookup_session")

    # ── Pricing calculation ───────────────────────────────────────
    section("3. Pricing Calculation")
    run("Q6", "How much would 20 seats on the Business plan cost monthly?",
        "pricing_session")
    run("Q7", "What's the annual cost for 10 Pro seats, and what do they save "
              "vs monthly billing?", "pricing_session")

    # ── Multi-tool chaining ───────────────────────────────────────
    section("4. Multi-Tool Chaining")
    run("Q8",
        "Look up customer C001 and calculate how much they'd save if they "
        "switched from monthly to annual billing.",
        "multi_session")

    # ── Email drafting ────────────────────────────────────────────
    section("5. Email Drafting")
    run("Q9",
        "Draft a support response email to customer C002 (Bob Martinez) letting "
        "him know his password reset request was processed and his account is "
        "ready to access.",
        "email_session")

    # ── Escalation ────────────────────────────────────────────────
    section("6. Escalation Ticket")
    run("Q10",
        "Customer C003 says her account was suspended by mistake and she needs "
        "it restored urgently — she has a client presentation in 2 hours.",
        "escalation_session")

    # ── Conversation memory ───────────────────────────────────────
    section("7. Conversation Memory")
    clear("memory_session")
    run("Q11", "What is the Business plan price?", "memory_session")
    run("Q12", "What about annual billing — how much does that save?",
        "memory_session")  # agent must remember "Business plan" from Q11
    run("Q13", "And how many seats does it include as standard?",
        "memory_session")  # tests multi-turn context retention

    # ── Edge cases ────────────────────────────────────────────────
    section("8. Edge Cases")
    run("Q14", "What plan is customer C999 on?", "edge_session")
    run("Q15", "How much does the Enterprise plan cost for 200 seats?",
        "edge_session")

    print(f"\n\n{'=' * 65}")
    print("  All tests complete.")
    print("=" * 65)


if __name__ == "__main__":
    main()