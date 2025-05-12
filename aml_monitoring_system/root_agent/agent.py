from google.adk.agents import Agent, SequentialAgent
from root_agent.sub_agents.data_collector_agent.agent import data_collector_agent
from root_agent.sub_agents.risk_analyzer_agent.agent import risk_analyzer_agent
from root_agent.sub_agents.alert_generator_agent.agent import alert_generator_agent
from root_agent.sub_agents.report_generator_agent.agent import report_generator_agent
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from dotenv import load_dotenv
load_dotenv()
# Create the root agent as a sequential agent that orchestrates the sub-agents 
root_agent = SequentialAgent(
    name="root_agent",
    description="AML Monitoring System - Detects suspicious activities, analyzes risks, generates alerts, and creates SAR reports.",
    sub_agents=[data_collector_agent, risk_analyzer_agent, alert_generator_agent, report_generator_agent]
)