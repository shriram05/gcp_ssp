from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from tools.risk_score_calculator import calculate_risk_score, check_risk_threshold

# Create FunctionTools
risk_calculator_tool = FunctionTool(calculate_risk_score)
threshold_checker_tool = FunctionTool(check_risk_threshold)

PROMPT = """
# Risk Analyzer Agent
You are an autonomous AML (Anti-Money Laundering) risk analyzer agent.

Responsibilities:
1. Calculate risk scores for customers based on suspicious activities:
   - Receive suspicious activity data from the Data Collector Agent
   - Determine the risk level using the `risk_calculator_tool`
   - Update the customer's risk score in the database

2. Check if a customer's risk score exceeds the threshold:
   - Use the `threshold_checker_tool` to determine if an alert should be triggered
   - If threshold is exceeded, flag the customer for review

3. Provide a clear risk assessment:
   - Explain why the risk score was increased
   - Show the previous and current risk scores
   - Indicate if the threshold has been exceeded

Always maintain accurate records and ensure all risk scores are properly calculated and stored.
"""

risk_analyzer_agent = Agent(
    name="risk_analyzer_agent",
    model="gemini-2.0-flash-lite",
    description="Calculates and analyzes risk scores based on suspicious activities.",
    tools=[risk_calculator_tool, threshold_checker_tool],
    instruction=PROMPT
)