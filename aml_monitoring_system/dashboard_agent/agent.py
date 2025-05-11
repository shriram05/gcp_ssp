from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from dashboard_agent.sub_agents.dashboard_frequent_small_agent import dashboard_frequent_small_agent
from dashboard_agent.sub_agents.dashboard_large_amount_agent import dashboard_large_amount_agent
from dashboard_agent.sub_agents.dashboard_multiple_location_agent import dashboard_multiple_location_agent
from dashboard_agent.sub_agents.dashboard_risk_agent import dashboard_risk_agent
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from dotenv import load_dotenv
load_dotenv()
# Create the root agent as a sequential agent that orchestrates the sub-agents 
transaction_agent = ParallelAgent(
    name="transaction_agent",
    description="Analayze different patterns of transaction",
    sub_agents=[ dashboard_large_amount_agent, dashboard_frequent_small_agent, dashboard_multiple_location_agent]
)

dashboard_agent=SequentialAgent(
    name="dashboard_agent",
    description="Analyze different patterns of transaction and provide risk analysis",
    sub_agents=[transaction_agent, dashboard_risk_agent]
)