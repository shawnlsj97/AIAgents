from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama
from phi.utils.pprint import pprint_run_response
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from typing import Iterator

# https://github.com/agno-agi/agno/blob/main/cookbook/playground/ollama_agents.py

# Initialize Ollama with Llama 3.1
ollama_model = Ollama(id="llama3.1")

web_agent = Agent(
    name="Web Agent",
    role="Retrieve and summarize web search results", # clarify agent's specialization
    model=ollama_model,
    tools=[DuckDuckGo()],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True
)

# Create an agent using Ollama model
finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=ollama_model,
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
    show_tool_calls=True,
    markdown=True,
    # debug_mode=True,
    instructions=[
        "Use tables to display data"
    ] # Agent-specific instructions
)

agent_team = Agent(
    team=[web_agent, finance_agent],
    model=ollama_model,
    instructions=["Always include sources", "Use tables to display data"], # Shared/global instructions among all agents
    show_tool_calls=True,
    markdown=True
)

# agent_team.print_response("Summarize analyst recommendations and share the latest news for NVDA")

response_stream: Iterator[RunResponse] = agent_team.run("Summarize analyst recommendations and share the latest news for NVDA", stream = True)
pprint_run_response(response_stream, markdown=True)
