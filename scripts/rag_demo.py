import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import ask

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


def main():
    print("=" * 70)
    print("RAG DEMO — TechFlow Knowledge Base Q&A")
    print("=" * 70)

    for i, question in enumerate(QUESTIONS, 1):
        print(f"\n[Q{i}] {question}")
        print("-" * 50)
        result = ask(question)
        print(result["answer"])
        print(f"\n  Sources retrieved: {len(result['sources_used'])}")
        for s in result["sources_used"][:2]:
            print(f"    - {s['source']} | {s['category']} | distance: {s['distance']}")


if __name__ == "__main__":
    main()