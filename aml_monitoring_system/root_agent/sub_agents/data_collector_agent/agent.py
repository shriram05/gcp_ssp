from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)
from root_agent.tools.large_amount_detector import detect_large_amount_transactions
from root_agent.tools.frequent_transaction_detector import detect_frequent_small_transactions
from root_agent.tools.multiple_location_detector import detect_multiple_location_transactions
from dotenv import load_dotenv
load_dotenv()

# Create FunctionTools
large_amount_tool = FunctionTool(detect_large_amount_transactions)
frequent_transaction_tool = FunctionTool(detect_frequent_small_transactions)
multiple_location_tool = FunctionTool(detect_multiple_location_transactions)

PROMPT = """
# Data Collector Agent

You are an autonomous AML (Anti-Money Laundering) data collector agent.

Firstly, before starting the work, initialize the models using the API keys provided. The API keys are given in the environment variables.

## Responsibilities

1. Collect and analyze financial transaction data to identify suspicious patterns using the tools:
   - Large amount transactions (using the large_amount_tool)
   - Frequent small transactions (using the frequent_transaction_tool)
   - Transactions from multiple locations (using the multiple_location_tool)

2. When a user provides a customer ID:
   - Analyze that specific customer's transactions for suspicious patterns using the tools mentioned above.

## Data Handling Requirements (STRICT)

- ALWAYS PRESERVE the COMPLETE OUTPUT STRUCTURE of each tool.
- DO NOT OMIT or REFORMAT any part of the tool responses.
- When consolidating results:
  - INCLUDE **ALL FIELDS** exactly as returned by the tools.
  - NEVER remove, rename, or simplify fields like `original_id`, `customer_id_send`, `customer_id_dest`, `timestamp`, `amount`, `location`, etc.
- DO NOT summarize, restructure, or infer new fields unless explicitly instructed.

## Output Format

- When presenting or passing the output, **wrap each tool’s raw output in code blocks** or JSON blocks to preserve structure.
- If combining outputs, **return a full JSON list or dictionary** maintaining the full structure of every item from the tool output.

Follow all instructions exactly. Any deviation from the above data handling requirements is considered incorrect.
"""


data_collector_agent = Agent(
    name="data_collector_agent",
    model="gemini-2.0-flash",
    description="Collects and analyzes transaction data to identify suspicious patterns.",
    tools=[large_amount_tool, frequent_transaction_tool, multiple_location_tool],
    instruction=PROMPT,
    output_key="datacollectoroutput"
)
