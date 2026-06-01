import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.research_crew import run_research

COMPANIES = ["OpenAI", "Shopify", "Stripe"]


def main():
    print("=" * 70)
    print("CREWAI MULTI-AGENT RESEARCH SYSTEM")
    print("=" * 70)
    print("Running a 4-agent crew: Researcher → Financial Analyst → Risk Analyst → Writer")
    print("Sequential execution — each agent's output feeds the next.\n")

    for company in COMPANIES:
        print(f"\n{'=' * 70}")
        print(f"RESEARCHING: {company}")
        print("=" * 70)
        result = run_research(company)
        print(result)
        print()


if __name__ == "__main__":
    main()