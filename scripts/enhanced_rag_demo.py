import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import ask
from src.enhanced_rag import ask_enhanced

# Same 20 questions from Day 44
QUESTIONS = [
    "How do I connect TechFlow to Slack?",
    "What are the remote work hours policy?",
    "How much does the Business plan cost per user?",
    "I'm getting error code TF-401, what does it mean?",
    "Can I export my data if I cancel?",
    "How many PTO days do new employees get?",
    "Does TechFlow support SSO and which identity providers?",
    "What happens when I exceed my storage limit?",
    "How do I set up two-factor authentication?",
    "What is the refund policy for annual plans?",
    "How does AI task auto-assignment decide who to assign work to?",
    "Can I import projects from Asana?",
    "What integrations are available on the free Starter plan?",
    "How do I invite someone to my workspace?",
    "What is the API rate limit on the Business plan?",
    "How does billing work if I add a user mid-month?",
    "What are the parental leave benefits?",
    "How do I recover a deleted task?",
    "Does TechFlow have a startup discount program?",
    "What AI features can I turn off if I don't want them?"
]

# Queries that specifically test hybrid search advantage:
# exact error codes, specific numbers, precise product names
HYBRID_SPOTLIGHT = [
    "TF-429 error",
    "What is the rate limit for Enterprise plans?",
    "How much storage does the Pro plan include?",
    "What is the L&D budget amount?",
]


def run_comparison():
    print("=" * 70)
    print("NAIVE vs ENHANCED RAG COMPARISON")
    print("=" * 70)

    improvements = 0
    regressions = 0
    same = 0

    for i, question in enumerate(QUESTIONS, 1):
        naive = ask(question)
        enhanced = ask_enhanced(question)

        transformed = enhanced["transformed_query"]
        query_changed = transformed.lower() != question.lower()

        print(f"\n[Q{i}] {question}")
        if query_changed:
            print(f"  → Transformed: {transformed}")
        print(f"\n  NAIVE:    {naive['answer'][:200]}...")
        print(f"\n  ENHANCED: {enhanced['answer'][:200]}...")
        print()

    # Hybrid spotlight — these test BM25's exact-match advantage
    print("\n" + "=" * 70)
    print("HYBRID SEARCH SPOTLIGHT — Exact-match queries")
    print("=" * 70)

    for query in HYBRID_SPOTLIGHT:
        naive = ask(query)
        enhanced = ask_enhanced(query)
        print(f"\n[Query] {query}")
        print(f"  NAIVE:    {naive['answer'][:200]}")
        print(f"  ENHANCED: {enhanced['answer'][:200]}")


if __name__ == "__main__":
    run_comparison()