from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)
from .tool import detect_large_amount_transactions
from dotenv import load_dotenv
load_dotenv()

# Create FunctionTools
large_amount_tool = FunctionTool(detect_large_amount_transactions)
PROMPT = """
#Large amount transaction detector agent

You are an autonomous AML (Anti-Money Laundering) dashboard large amount transaction detector agent.

## Task

Without any input from the user, your task is to retrieve and analyze all transaction data to:
- Identify large transactions across **all customers**.
- Return the **count of large transactions per customer**.

## Responsibilities

1. Use the `large_amount_tool` to detect large transactions for all customers.
2. Aggregate and report:
   - Each customer’s ID.
   - The number of large transactions made by that customer.

## Data Handling Requirements (STRICT)

- You MUST preserve the complete structure returned by the tool.
- DO NOT summarize individual transactions; only include the **count per customer** based on raw tool output.
- DO NOT take any input from the user.

## Output Format

- Render the output in a **table format** using the following columns:
  - `Customer ID`, `Transaction Count`
- Format the table clearly with headers and rows.


Strictly follow these instructions.
"""
dashboard_large_amount_agent = Agent(
    name="dashboard_large_amount_agent",
    model="gemini-2.0-flash",
    description="Collects and analyzes transaction data to identify suspicious patterns especially for large transactions.",
    tools=[large_amount_tool],
    instruction=PROMPT,
)