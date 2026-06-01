from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)


# ── TOOLS ──────────────────────────────────────────────────────────────────────
# CrewAI tools use the same @tool decorator pattern as LangGraph.
# Each agent is given a subset of tools relevant to its role.

@tool("web_search")
def web_search(query: str) -> str:
    """
    Search the web for information about a company, industry, or topic.
    Use this to find recent news, company background, products, and market position.
    """
    # Simulated web search — returns realistic mock data based on query
    mock_results = {
        "openai": """
            OpenAI is an AI research company founded in 2015, valued at ~$80B.
            Products: ChatGPT (200M+ users), GPT-4, DALL-E, Whisper, Sora.
            Revenue: ~$2B ARR as of 2024, growing rapidly.
            Key developments: GPT-5 released 2025, partnership with Microsoft ($13B invested).
            Competitors: Anthropic, Google DeepMind, Meta AI.
            Risks: Regulatory scrutiny, compute costs, talent competition.
        """,
        "shopify": """
            Shopify is a Canadian e-commerce platform founded in 2006.
            Serves 2M+ merchants across 175 countries.
            Revenue: $7.06B in 2023, 26% YoY growth.
            Products: Online store builder, payments, shipping, POS, capital lending.
            Key developments: Sold logistics arm to Flexport in 2023 to refocus on software.
            Competitors: WooCommerce, BigCommerce, Salesforce Commerce Cloud.
            Risks: Competition from Amazon, economic slowdown affecting SMB merchants.
        """,
        "stripe": """
            Stripe is a payments infrastructure company founded in 2010.
            Processes $1T+ in payments annually.
            Valuation: $65B (2023 secondary market).
            Products: Payments, billing, fraud prevention, banking-as-a-service, Atlas.
            Key developments: Expanding into stablecoin payments, AI fraud detection.
            Competitors: PayPal, Square, Adyen, Braintree.
            Risks: Regulatory complexity across markets, interchange fee pressure.
        """
    }
    query_lower = query.lower()
    for key, result in mock_results.items():
        if key in query_lower:
            return result.strip()
    return f"Search results for '{query}': General market information available but no specific data found for this query."


@tool("financial_analyzer")
def financial_analyzer(company_data: str) -> str:
    """
    Analyze financial metrics and business model from company information.
    Provide revenue trends, growth rate, profitability indicators, and financial health assessment.
    Input should be a description or summary of the company's financial situation.
    """
    prompt_keywords = company_data.lower()

    if "openai" in prompt_keywords:
        return """
        Financial Analysis:
        - Revenue: ~$2B ARR, ~200% YoY growth
        - Business model: API subscriptions + ChatGPT Plus ($20/month)
        - Gross margins: Estimated 50-60% (high compute costs)
        - Cash position: Strong (Microsoft backing + VC funding)
        - Burn rate: High — inference costs at scale are significant
        - Financial health: STRONG growth trajectory, not yet profitable
        - Key metric to watch: Cost per query as models scale
        """
    elif "shopify" in prompt_keywords:
        return """
        Financial Analysis:
        - Revenue: $7.06B (2023), 26% YoY growth
        - Business model: Subscription + transaction fees (merchant solutions ~70% of revenue)
        - Gross margins: ~52% overall, software margins ~80%+
        - Free cash flow: Positive, improving post-logistics divestiture
        - Financial health: SOLID — profitable on operating basis
        - Key metric to watch: MRR per merchant as they move upmarket
        """
    elif "stripe" in prompt_keywords:
        return """
        Financial Analysis:
        - Revenue: Estimated $14B+ (2023), ~25% growth
        - Business model: Take rate on payment volume (~0.3% net)
        - Gross margins: ~60-70%
        - Profitability: Reportedly profitable at operating level since 2023
        - Financial health: STRONG — resilient to interest rate environment
        - Key metric to watch: Payment volume growth and international expansion
        """
    return "Insufficient data for detailed financial analysis. Provide specific company financial information."


@tool("risk_assessor")
def risk_assessor(company_name: str) -> str:
    """
    Assess key business, market, and operational risks for a company.
    Returns a structured risk profile with severity ratings.
    """
    risks = {
        "openai": [
            ("Regulatory risk", "HIGH", "EU AI Act, potential US regulation of frontier AI models"),
            ("Compute dependency", "HIGH", "Relies heavily on NVIDIA GPUs — supply constraints affect scaling"),
            ("Competition", "MEDIUM", "Anthropic, Google Gemini, and open-source models closing capability gap"),
            ("Key person risk", "MEDIUM", "Sam Altman departure in 2023 demonstrated governance fragility"),
            ("Revenue concentration", "LOW", "Diversifying across API, enterprise, consumer — reducing single-product risk"),
        ],
        "shopify": [
            ("SMB sensitivity", "HIGH", "Core customer base vulnerable to economic downturns"),
            ("Amazon competition", "HIGH", "Amazon's fulfillment and marketplace advantages are structural"),
            ("Take rate pressure", "MEDIUM", "Merchants increasingly price-sensitive on transaction fees"),
            ("International expansion", "MEDIUM", "Currency risk and regulatory complexity in new markets"),
            ("Platform dependency", "LOW", "Merchants building on Shopify create switching costs"),
        ],
        "stripe": [
            ("Regulatory risk", "HIGH", "Payment regulations vary significantly by country — compliance cost is high"),
            ("Fraud exposure", "MEDIUM", "Increasing sophisticated fraud attempts despite ML detection"),
            ("Competition from banks", "MEDIUM", "Traditional financial institutions building competing infrastructure"),
            ("IPO pressure", "LOW", "Private investors expecting liquidity — timing of public offering uncertain"),
            ("Chargeback liability", "LOW", "Structural risk managed through fraud tools and merchant agreements"),
        ]
    }
    company_lower = company_name.lower()
    for key, risk_list in risks.items():
        if key in company_lower:
            output = f"Risk Assessment for {company_name}:\n\n"
            for risk, severity, detail in risk_list:
                output += f"[{severity}] {risk}: {detail}\n"
            return output
    return f"Risk data not available for {company_name}. General market risks apply."


# ── AGENTS ─────────────────────────────────────────────────────────────────────
# Each agent has a role, goal, and backstory.
# Role: what the agent is
# Goal: what it's trying to achieve
# Backstory: context that shapes how it reasons and communicates

def build_crew(company_name: str) -> Crew:

    researcher = Agent(
        role="Senior Market Research Analyst",
        goal=f"Gather comprehensive, accurate information about {company_name} "
             f"including their products, market position, recent developments, and competitive landscape.",
        backstory="""You are a senior analyst at a top-tier consulting firm with 15 years of experience
        researching technology companies. You are thorough, skeptical of hype, and always verify
        claims with specific data points. Your research forms the foundation that all other
        team members depend on — accuracy is non-negotiable.""",
        tools=[web_search],
        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter = 5
    )

    financial_analyst = Agent(
        role="Financial Intelligence Analyst",
        goal=f"Analyze {company_name}'s financial health, business model, revenue streams, "
             f"and growth trajectory to assess investment and partnership viability.",
        backstory="""You are a financial analyst specializing in technology sector valuations.
        You cut through narrative to focus on unit economics, margins, and cash flow.
        You translate complex financial data into clear business implications.
        You never speculate — if data is unavailable, you say so explicitly.""",
        tools=[financial_analyzer],
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    risk_analyst = Agent(
        role="Risk Intelligence Specialist",
        goal=f"Identify and assess the key business, regulatory, operational, and market risks "
             f"facing {company_name}, with clear severity ratings and mitigation context.",
        backstory="""You are a risk specialist with backgrounds in both consulting and regulatory compliance.
        You have a talent for identifying risks that optimistic analysts overlook.
        You present risks clearly and without alarmism — your job is to inform decisions, not create panic.
        You always rate risks by severity and explain the reasoning.""",
        tools=[risk_assessor],
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    writer = Agent(
        role="Strategic Intelligence Writer",
        goal=f"Synthesize all research, financial analysis, and risk assessment into a clear, "
             f"professional executive brief about {company_name} that a senior decision-maker "
             f"can act on in under 5 minutes.",
        backstory="""You are a former McKinsey consultant turned business writer. You have written
        hundreds of executive briefings for C-suite audiences. You know that executives don't read —
        they scan. Your briefs lead with the most important insight, use plain language,
        and end with a clear recommendation. You never pad content or repeat yourself.""",
        tools=[],  # Writer synthesizes — no external tools needed
        llm=llm,
        verbose=False,
        allow_delegation=False
    )

    # ── TASKS ──────────────────────────────────────────────────────────────────
    # Tasks define what each agent must produce.
    # expected_output tells the agent exactly what format the output should take.
    # context=[...] passes the output of one task as input to the next.

    research_task = Task(
        description=f"""Research {company_name} thoroughly. Use the web_search tool to gather:
        1. Company background (founded, headquarters, team size)
        2. Core products and services
        3. Market position and key competitors
        4. Recent significant developments (last 12 months)
        5. Customer base and target market
        Be specific — include numbers, dates, and named competitors where available.""",
        expected_output=f"""A structured research summary of {company_name} with 5 clearly labeled sections:
        Background, Products/Services, Market Position, Recent Developments, and Customer Base.
        Each section should be 3-5 sentences with specific facts and figures.""",
        agent=researcher
    )

    financial_task = Task(
        description=f"""Analyze the financial health and business model of {company_name}.
        Use the financial_analyzer tool with the company name and any financial data
        from the research output. Assess: revenue, growth rate, margins, profitability,
        and overall financial health. Be direct about what is unknown.""",
        expected_output=f"""A financial analysis of {company_name} covering:
        Revenue and growth trajectory, Business model and margin structure,
        Profitability status, Key financial metrics to monitor, and
        an overall financial health rating (STRONG / STABLE / CONCERNING).""",
        agent=financial_analyst,
        context=[research_task]
    )

    risk_task = Task(
        description=f"""Assess the key risks facing {company_name}.
        Use the risk_assessor tool with the company name.
        Present risks with severity ratings (HIGH/MEDIUM/LOW) and explain
        the business implication of each. Identify the single most critical risk.""",
        expected_output=f"""A risk profile for {company_name} with:
        - 3-5 risks rated HIGH/MEDIUM/LOW with one-sentence explanations
        - The single most critical risk highlighted
        - One sentence on overall risk posture""",
        agent=risk_analyst,
        context=[research_task]
    )

    writing_task = Task(
        description=f"""Write an executive intelligence brief on {company_name} for a senior
        decision-maker considering whether to partner with or invest in this company.
        Synthesize the research, financial analysis, and risk assessment into a
        single coherent brief. Lead with the most important insight.
        End with a clear recommendation: PROCEED / PROCEED WITH CAUTION / AVOID.""",
        expected_output=f"""A professional executive brief on {company_name} with these sections:
        1. One-line verdict (PROCEED / PROCEED WITH CAUTION / AVOID)
        2. Company snapshot (3 sentences max)
        3. Financial health (3 sentences max)
        4. Key risks (bullet list, 3 items max)
        5. Recommendation rationale (2-3 sentences)
        Total length: under 300 words. Professional tone. No filler.""",
        agent=writer,
        context=[research_task, financial_task, risk_task]
    )

    crew = Crew(
        agents=[researcher, financial_analyst, risk_analyst, writer],
        tasks=[research_task, financial_task, risk_task, writing_task],
        process=Process.sequential,
        verbose=False
    )

    return crew


def run_research(company_name: str) -> str:
    """Run the research crew on a company and return the final brief."""
    crew = build_crew(company_name)
    result = crew.kickoff()
    return str(result)