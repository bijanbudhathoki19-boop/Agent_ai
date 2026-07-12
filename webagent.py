import os
from dotenv import load_dotenv

from agno.team import Team
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.tavily import TavilyTools

load_dotenv()

# ==========================================================
# LLM
# ==========================================================

model = Groq(
    id="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
)

# ==========================================================
# BUILD AGENT
# ==========================================================

build_agent = Agent(
    name="Build Agent",
    role="Senior Software Engineer",
    model=model,
    instructions="""
You are an expert software engineer.

Expertise:
- Python
- FastAPI
- Django
- React
- Streamlit
- APIs
- SQL
- LangChain
- LangGraph
- CrewAI
- Agno
- AI/ML
- System Design

Return production-ready solutions.
""",
)

# ==========================================================
# FINANCE AGENT
# ==========================================================

finance_agent = Agent(
    name="Finance Agent",
    role="Financial Advisor",
    model=model,
    instructions="""
You are a finance expert.

Help with:
- budgeting
- investing
- business finance
- financial analysis
- accounting
- stock market
- crypto
- taxation

Explain calculations clearly.
""",
)

# ==========================================================
# MARKETING AGENT
# ==========================================================

marketing_agent = Agent(
    name="Marketing Agent",
    role="Marketing Expert",
    model=model,
    instructions="""
You are a marketing specialist.

Help with

- SEO
- Branding
- Social Media
- Marketing Campaigns
- Email Marketing
- Product Launch
- Content Creation
- Sales Funnel

Always provide actionable advice.
""",
)

# ==========================================================
# WEB AGENT
# ==========================================================

web_agent = Agent(
    name="Web Search Agent",
    role="Research Expert",
    model=model,
    tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))],
    instructions="""
Search the web whenever current or factual information is required.

Always provide concise summaries with sources.
""",
)

# ==========================================================
# MASTER AGENT
# ==========================================================

master =  Team(
    name="Master Agent",
    model=model,
    members=[
        build_agent,
        finance_agent,
        marketing_agent,
        web_agent,
    ],
    instructions="""
You are an intelligent orchestrator.

Your job is to understand the user's intent.

Delegate the work to the correct specialist.

Rules:

- Software/programming → Build Agent

- Finance/investments/accounting → Finance Agent

- Marketing/branding/SEO → Marketing Agent

- Current events/latest information/research → Web Search Agent

If multiple domains are involved,
delegate to multiple agents.

Examples:

User:
Build an ecommerce website and create a marketing plan.

Use:
- Build Agent
- Marketing Agent

----------------------

User:
Create a fintech app and estimate the development cost.

Use:
- Build Agent
- Finance Agent

----------------------

User:
Research Tesla stock and summarize today's news.

Use:
- Finance Agent
- Web Search Agent

----------------------

User:
Create an AI startup from scratch.

Use

- Build Agent
- Finance Agent
- Marketing Agent
- Web Search Agent

Combine all responses into one professional answer.
""",
    markdown=True,
)

# ==========================================================
# CHAT LOOP
# ==========================================================

print("=" * 60)
print("🤖 Multi-Agent AI")
print("Type 'exit' to quit")
print("=" * 60)

while True:

    query = input("\nYou : ")

    if query.lower() == "exit":
        break

    response = master.run(query)

    print("\nAI:\n")
    print(response.content)