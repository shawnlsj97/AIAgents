from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama
from phi.utils.pprint import pprint_run_response
from phi.tools.yfinance import YFinanceTools
from typing import Iterator

# Initialize Ollama with Llama 3.1
ollama_model = Ollama(id="llama3.1")

def get_company_symbol(company: str) -> str:
    """Use this function to get the symbol for a company. Data is stored as "CompanyName": "Symbol" pairs in the dictionary. For example, "Phidata" should resolve to "NVDA".

    Args:
        company (str): The name of the company.

    Returns:
        str: The symbol for the company.
    """
    symbols = {
        "Phidata": "NVDA",
        "Infosys": "INFY",
        "Tesla": "TSLA",
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Amazon": "AMZN",
        "Google": "GOOGL",
    }
    return symbols.get(company, "Unknown")

# Create an agent using Ollama model
agent = Agent(
    model=ollama_model,
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, stock_fundamentals=True),  get_company_symbol],
    show_tool_calls=True,
    markdown=True,
    # debug_mode=True,
    instructions=[
        "Use tables to display data",
        "Use get_company_symbol tool to find the symbol for companies, then use the symbol to retrieve recommendations and fundamentals from yfinance.",
    ]
)

# agent.print_response("Summarize and compare analyst recommendations and fundamentals for Tesla and Phidata.")

response_stream: Iterator[RunResponse] = agent.run("Summarize and compare analyst recommendations and fundamentals for Tesla and Phidata.", stream = True)
pprint_run_response(response_stream, markdown=True)
