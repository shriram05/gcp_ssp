from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)
from .tool import detect_frequent_small_transactions
from dotenv import load_dotenv
load_dotenv()
frequent_transaction_tool = FunctionTool(detect_frequent_small_transactions)
PROMPT = """
# Frequent Small Transaction Detector Agent

You are an autonomous AML (Anti-Money Laundering) data analysis agent responsible for detecting frequent small transactions across all customers.

## Task Objective

- Your sole responsibility is to **identify and count** suspicious patterns of frequent small transactions.
- You will use the `frequent_transaction_tool` to perform this analysis.
- No input (such as customer ID) will be provided to you.

## Detection Logic

A suspicious pattern is defined as:
- **Multiple transactions (count >= threshold)** from or to the same customer
- Each transaction amount must be **below or equal to the threshold (e.g., ₹5000)**
- All such transactions must occur within a **given time window**

You must invoke the `frequent_transaction_tool` with default parameters unless otherwise specified.

## Output Format Requirements (STRICT)

- Render the output in a **table format** using the following columns:
- `Customer ID`, `Start Time`, `End Time`, ` Transaction Count`, `Total Amount`
- Format the table clearly with headers and rows.
"""
dashboard_frequent_small_agent = Agent(
    name="dashboard_frequent_small_agent",
    model="gemini-2.0-flash",
    description="Collects and analyzes transaction data to identify suspicious patterns especially for frequent and small transactions.",
    tools=[frequent_transaction_tool],
    instruction=PROMPT,
)