from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)
from root_agent.tools.large_amount_detector import detect_large_amount_transactions
from root_agent.tools.frequent_transaction_detector import detect_frequent_small_transactions
from root_agent.tools.multiple_location_detector import detect_multiple_location_transactions

# Create FunctionTools
large_amount_tool = FunctionTool(detect_large_amount_transactions)
frequent_transaction_tool = FunctionTool(detect_frequent_small_transactions)
multiple_location_tool = FunctionTool(detect_multiple_location_transactions)

PROMPT = """
# Data Collector Agent
You are an autonomous AML (Anti-Money Laundering) data collector agent.

Responsibilities:
1. Collect and analyze financial transaction data to identify suspicious patterns:
   - Large amount transactions (using the large_amount_tool)
   - Frequent small transactions (using the requent_transaction_tool)
   - Transactions from multiple locations (using the multiple_location_tool)

2. When a user provides a customer ID:
   - Analyze that specific customer's transactions for suspicious patterns
   - If no customer ID is provided, analyze all customers

3. Format and consolidate all suspicious activity findings:
   - Group findings by customer
   - Present a clear summary of all suspicious activities detected
   - Highlight the most concerning patterns

Use the provided tools to detect suspicious patterns. Be thorough and accurate in your analysis.
"""

data_collector_agent = Agent(
    name="data_collector_agent",
    model="gemini-2.0-flash-lite",
    description="Collects and analyzes transaction data to identify suspicious patterns.",
    tools=[large_amount_tool, frequent_transaction_tool, multiple_location_tool],
    instruction=PROMPT
)
