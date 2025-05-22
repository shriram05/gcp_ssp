# import json
# from vertexai import agent_engines

# # List all agents in the current project/region
# agents = agent_engines.list()

# for agent in agents:
#     print("="*60)
#     print("Testing agent:", agent.resource_name)
#     print("Supported operations:", [op["name"] for op in agent.operation_schemas()])
    
#     # Only proceed if the agent supports the required streaming operation
#     if "streaming_agent_run_with_events" in [op["name"] for op in agent.operation_schemas()]:
#         try:
#             # Create a session
#             session = agent.create_session(user_id="user_1")
            
#             # Prepare the request payload
#             request = {
#                 "user_id": "user_1",
#                 "session_id": session["id"],
#                 "message": "Hello"
#             }
#             request_json = json.dumps(request)
            
#             # Call the streaming operation and print all events
#             print("Streaming events:")
#             has_event = False
#             for event in agent.streaming_agent_run_with_events(request_json=request_json):
#                 print(event)
#                 has_event = True
#             if not has_event:
#                 print("No events received from this agent.")
#         except Exception as e:
#             print(f"Error while querying agent: {e}")
#     else:
#         print("This agent does not support 'streaming_agent_run_with_events'.")
#     print("="*60)

import os
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
# from root_agent.agent import root_agent
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


# def create_local_agent():
#     local_agent = reasoning_engines.AdkApp(
#         agent=root_agent,
#         enable_tracing=True
#     )
#     return local_agent


# remote_agent = agent_engines.create(
#         agent_engine=create_local_agent(),
#         requirements=[
#             "google-cloud-aiplatform[adk,agent_engines]"
#         ]
#     )
# agent_resource_name = remote_agent.resource_name


# agent = agent_engines.get("projects/1013958054897/locations/us-central1/reasoningEngines/5127145865621798912")
# current_session = agent.create_session(user_id="user_1")
# print(current_session)
# print("============================================")
# def connect_to_agent(agent_resource_name):
#     try:
#         agent = agent_engines.get(agent_resource_name)
#         print(f"Connected to agent: {agent_resource_name}")
#     except Exception as e:
#         agent = None
#         print(f"Failed to connect to agent: {e}")
#     return agent

# def run_agent(agent, message):        
#     if agent:
#         try:
#             current_session = agent.create_session(user_id="test_user_1")

#             for event in agent.stream_query(
#                 user_id="test_user_1",
#                 session_id=current_session["id"],
#                 message=message
#             ):
#                 return event
#         except Exception as e:
#             print(f"Error during agent interaction: {e}")
#     else: 
#         print("Skipping process as agent doesn't exist.")

# # agent_resource_name = deploy_agent()

# agent_resource_name = "projects/1013958054897/locations/us-central1/reasoningEngines/5127145865621798912"

# agent = connect_to_agent(agent_resource_name)

# event = run_agent(agent, "C10045")

# # response = event["content"]["parts"][0]["text"]

# print(f"Agent Response: {event}")

from vertexai import agent_engines
import json

def connect_to_agent(agent_resource_name):
    try:
        agent = agent_engines.get(agent_resource_name)
        print(f"Connected to agent: {agent_resource_name}")
        return agent
    except Exception as e:
        print(f"Failed to connect to agent: {e}")
        return None

def run_agent(agent, message):        
    if not agent:
        print("Agent not initialized. Skipping process.")
        return None
    
    try:
        # Create a session
        session = agent.create_session(user_id="test_user_1")
        data = {
    "user_id": "test_user_1",
    "session_id": session["id"],
    "new_message": {
        "role": "user",
        "parts": [{
            "text": message
        }]
        },
        "streaming": False
    }
        
        # Prepare request payload (JSON string)
        # request = {
        #     "user_id": "test_user_1",
        #     "session_id": session["id"],
        #     "message": message
        # }
        request_json = json.dumps(data)
        
        # Stream events using the CORRECT method name
        events = []
        for event in agent.streaming_agent_run_with_events(request_json=request_json):
            events.append(event)
        
        return events
    except Exception as e:
        print(f"Error during agent interaction: {str(e)}")
        return None

# Test
agent_resource_name = "projects/1013958054897/locations/us-central1/reasoningEngines/5127145865621798912"
agent = connect_to_agent(agent_resource_name)
response = run_agent(agent, "Hi, how are you?")

if response:
    print("Agent Response Events:")
    for event in response:
        print(event)
else:
    print("No response received.")

 


