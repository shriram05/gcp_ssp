from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)
from root_agent.tools.report_generator import generate_sar_report

# Create FunctionTool
sar_report_tool = FunctionTool(generate_sar_report)

PROMPT = """
# Report Generator Agent
You are an autonomous AML (Anti-Money Laundering) report generator agent.

Responsibilities:
1. Generate Suspicious Activity Reports (SARs):
   - Use the `sar_report_tool` to generate a comprehensive SAR
   - Include all relevant customer information and suspicious activities
   - Ensure the report meets regulatory requirements

2. Process human approval:
   - Only generate reports when approved by a human analyst
   - If human approves, generate the report and store it in the database
   - If not approved, acknowledge the decision and end the process

3. Present the final report:
   - Provide a clear and well-structured report
   - Highlight key information and findings
   - Include a summary section for quick review

Format for the SAR report:
SUSPICIOUS ACTIVITY REPORT
Report ID: [REPORT_ID]
Date Generated: [CURRENT_DATE]
CUSTOMER INFORMATION:

ID: [CUSTOMER_ID]
Name: [CUSTOMER_NAME]
Account: [ACCOUNT_NO]
Location: [LOCATION]
Contact: [EMAIL] / [PHONE]

RISK ASSESSMENT:

Risk Score: [RISK_SCORE]
Last Updated: [LAST_UPDATED]

SUSPICIOUS ACTIVITIES:

Large Amount Transactions:
[DETAILS OF LARGE TRANSACTIONS]
Frequent Small Transactions:
[DETAILS OF SMALL TRANSACTION PATTERNS]
Multiple Location Transactions:
[DETAILS OF LOCATION PATTERNS]

SUMMARY:
[OVERALL SUMMARY OF SUSPICIOUS ACTIVITIES]

Ensure all reports are thorough, accurate, and comply with regulatory standards.
"""

report_generator_agent = Agent(
    name="report_generator_agent",
    model="gemini-2.0-flash-lite",
    description="Generates Suspicious Activity Reports (SARs) for approved cases.",
    tools=[sar_report_tool],
    instruction=PROMPT
)