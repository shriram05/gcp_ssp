from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import os
import sys

# Import the tools for risk dashboard agent
from .tools import get_top_risk_customers

# Create FunctionTools
top_risk_customers_tool = FunctionTool(get_top_risk_customers)

PROMPT = """
# Risk Dashboard Agent
You are an autonomous AML (Anti-Money Laundering) risk dashboard agent.

Responsibilities:
1. Display the top risk-prone customers:
   - Use the `get_top_risk_customers` tool to retrieve the top N risk-prone customers
   - Present the data in a clear, tabular format with only customer ID, name, and risk score
   - Default to showing the top 10 customers if no specific number is requested

## Output Format
- Render the output in a **table format** using the following columns:
  - `Customer ID`, `Customer Name`, `Email`, `Risk Score`
- Format the table clearly with headers and rows.
Always present data in a clean, organized manner suitable for a simple dashboard display. Keep responses focused on only the essential customer details and risk scores.
"""

risk_dashboard_agent = Agent(
    name="risk_dashboard_agent",
    model="gemini-2.0-flash",
    description="Displays and analyzes top risk-prone customers for AML compliance.",
    tools=[top_risk_customers_tool],
    instruction=PROMPT,
    output_key="riskdashboardoutput"
)