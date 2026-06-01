import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.langchain_rag import load_documents, build_vectorstore, build_rag_chain, ask_langchain
from src.rag import ask as ask_scratch

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
    # Build vector store (only needed once — skip if .chroma_lc already exists)
    lc_dir = Path(".chroma_lc")
    documents = load_documents()

    if not lc_dir.exists():
        print("Building LangChain vector store...")
        vectorstore = build_vectorstore(documents)
    else:
        print("Loading existing LangChain vector store...")
        from src.langchain_rag import load_vectorstore
        vectorstore = load_vectorstore()

    chain, _ = build_rag_chain(vectorstore)

    print("\n" + "=" * 70)
    print("LANGCHAIN RAG vs FROM-SCRATCH RAG")
    print("=" * 70)

    for i, question in enumerate(QUESTIONS, 1):
        lc_result = ask_langchain(question, chain)
        scratch_result = ask_scratch(question)

        print(f"\n[Q{i}] {question}")
        print(f"  SCRATCH:    {scratch_result['answer'][:200]}")
        print(f"  LANGCHAIN:  {lc_result['answer'][:200]}")

    print("\n✅ Comparison complete.")


if __name__ == "__main__":
    main()