import os
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from .agent import root_agent
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
STAGING_BUCKET = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)


def create_local_agent():
    local_agent = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True
    )
    return local_agent


try:
    remote_agent = agent_engines.create(
    agent_engine=create_local_agent(),
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]"
    ],
    extra_packages=["root_agent"]  # 👈 tells Vertex to send this folder
    )

    agent_resource_name = remote_agent.resource_name
    agent = agent_engines.get(agent_resource_name)
    
    print(f"Attempting to create session for agent: {agent_resource_name}")
    current_session = agent.create_session(user_id="user_1")
    print(f"Session created successfully: {current_session}")
except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()