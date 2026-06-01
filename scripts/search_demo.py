import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.search import semantic_search

TEST_QUERIES = [
    "How do I connect TechFlow to Slack?",
    "What are the remote work rules?",
    "How much does the enterprise plan cost?",
    "I'm getting a login error, what should I do?",
    "Can I export my project data?",
    "How many days of PTO do employees get?",
    "What integrations does TechFlow support?",
    "How do I reset my password?",
    "What is the refund policy?",
    "How does task auto-assignment work?",
    "Can I use TechFlow on mobile?",
    "What happens if I exceed my storage limit?",
    "How do I invite team members?",
    "Is there a free trial available?",
    "What security certifications does TechFlow have?",
    "How do I cancel my subscription?",
    "Can I import data from Asana?",
    "What are the core hours for remote workers?",
    "How does billing work for annual plans?",
    "What AI features does TechFlow include?"
]


def main():
    print("=" * 60)
    print("SEMANTIC SEARCH DEMO — TechFlow Knowledge Base")
    print("=" * 60)

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"\n[Query {i}] {query}")
        print("-" * 40)
        results = semantic_search(query, n_results=3)
        for result in results:
            print(f"  Rank {result['rank']} | {result['category']} | distance: {result['distance']}")
            print(f"  {result['text'][:120]}...")
        print()


if __name__ == "__main__":
    main()