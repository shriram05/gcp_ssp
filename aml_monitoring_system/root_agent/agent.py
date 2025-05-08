from google.adk.agents import Agent, SequentialAgent
from sub_agents.data_collector_agent.agent import data_collector_agent
from sub_agents.risk_analyzer_agent.agent import risk_analyzer_agent
from sub_agents.alert_generator_agent.agent import alert_generator_agent
from sub_agents.report_generator_agent.agent import report_generator_agent

# Create the root agent as a sequential agent that orchestrates the sub-agents
root_agent = SequentialAgent(
    name="aml_monitoring_agent",
    description="AML Monitoring System - Detects suspicious activities, analyzes risks, generates alerts, and creates SAR reports.",
    sub_agents=[data_collector_agent, risk_analyzer_agent, alert_generator_agent, report_generator_agent]
)