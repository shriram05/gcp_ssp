from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from dashboard_agent.sub_agents.dashboard_large_amount_agent.agent import dashboard_large_amount_agent
from dashboard_agent.sub_agents.dashboard_frequent_small_agent.agent import dashboard_frequent_small_agent
from dashboard_agent.sub_agents.dashboard_multiple_location_agent.agent import dashboard_multiple_location_agent

import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from dotenv import load_dotenv
load_dotenv()
# Create the root agent as a sequential agent that orchestrates the sub-agents 
dashboard_agent=ParallelAgent(
    name="transaction_agent",
    description="Analyze different patterns of transaction",
    sub_agents=[dashboard_large_amount_agent, dashboard_frequent_small_agent, dashboard_multiple_location_agent]
)

