import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import run_agent

# These queries test different routing paths through the graph
TEST_QUERIES = [
    # Knowledge base queries — tests search_knowledge_base tool
    "What integrations does TechFlow support?",
    "What is the refund policy for annual plans?",
    "How does AI task auto-assignment work?",

    # Customer lookup — tests lookup_customer tool
    "Can you pull up the account for customer C001?",
    "What plan is customer C002 on?",

    # Pricing calculation — tests calculate_price tool
    "How much would 15 seats on the Business plan cost monthly?",
    "What's the annual cost for 8 Pro plan seats?",

    # Multi-tool — tests chaining two tools in one query
    "Look up customer C001 and tell me how much they'd save switching to annual billing.",

    # Escalation — tests human-in-the-loop approval flow
    "Customer C003 says their account was suspended by mistake and they need it restored immediately.",

    # Edge cases
    "What plan is customer C999 on?",           # non-existent customer
    "How much does the Enterprise plan cost for 50 seats?",  # custom pricing
    "What is the L&D budget for employees?",    # policy question
    "How do I set up SSO with Okta?",           # support question
    "Calculate the price for 100 business seats annually.",
    "Does TechFlow have a startup program?",
]


def main():
    print("=" * 70)
    print("LANGGRAPH AGENT DEMO — TechFlow Support Agent")
    print("=" * 70)
    print("Note: The escalation query will pause and ask for your approval.\n")

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n[Q{i}] {query}")
        print("-" * 50)
        try:
            response = run_agent(query)
            print(response)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()