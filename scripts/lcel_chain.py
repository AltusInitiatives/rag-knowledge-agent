import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

load_dotenv()


# Define the structured output schema using Pydantic
class TaskClassification(BaseModel):
    category: str = Field(description="One of: bug, feature_request, question, complaint, compliment")
    priority: str = Field(description="One of: high, medium, low")
    sentiment: str = Field(description="One of: positive, neutral, negative")
    summary: str = Field(description="One sentence summary of the input")


def build_classifier_chain():
    """
    LCEL chain that takes raw customer input and returns structured JSON.
    This pattern is used constantly in real automation work —
    raw text in, structured data out.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = JsonOutputParser(pydantic_object=TaskClassification)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a customer support classifier for TechFlow.
Classify the customer message and respond with valid JSON matching this schema:
{format_instructions}"""),
        ("human", "{input}")
    ]).partial(format_instructions=parser.get_format_instructions())

    # The chain: prompt → LLM → parse to structured dict
    chain = prompt | llm | parser
    return chain


TEST_INPUTS = [
    "I can't log in and I have a presentation in 20 minutes, this is urgent!",
    "Love the new dashboard update, it's so much faster now.",
    "How do I export my data to CSV?",
    "The API keeps returning 429 errors even though I'm well under my limit.",
    "Would be great if you could add a dark mode option.",
]


def main():
    chain = build_classifier_chain()

    print("=" * 60)
    print("LCEL CLASSIFIER CHAIN — Structured Output Demo")
    print("=" * 60)

    for text in TEST_INPUTS:
        result = chain.invoke({"input": text})
        print(f"\nInput: {text[:80]}")
        print(f"  Category:  {result['category']}")
        print(f"  Priority:  {result['priority']}")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Summary:   {result['summary']}")


if __name__ == "__main__":
    main()