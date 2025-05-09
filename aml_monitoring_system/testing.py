# import os
# import json
# import asyncio
# import inspect
# from typing import Any, Dict, List, Optional
# from dotenv import load_dotenv
# from root_agent.agent import root_agent
# from root_agent.context import InvocationContext  # Import the actual context class

# def initialize_google_cloud():
#     """
#     Initialize Google Cloud and Vertex AI services using environment variables.
#     """
#     # Load environment variables from .env file
#     load_dotenv()
    
#     # Set up Google Cloud credentials
#     credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
#     project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
#     vertex_location = os.environ.get('VERTEX_LOCATION')
#     gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
#     print(f"Credentials path: {credentials_path}")
#     print(f"Project ID: {project_id}")
#     print(f"Vertex AI location: {vertex_location}")
#     print(f"Gemini API key available: {'Yes' if gemini_api_key else 'No'}")
    
#     # Ensure credentials file exists
#     if credentials_path and not os.path.isfile(credentials_path):
#         print(f"Warning: Credentials file not found at {credentials_path}")
    
#     # Initialize Vertex AI if available
#     try:
#         import google.cloud.aiplatform as vertexai
#         vertexai.init(project=project_id, location=vertex_location)
#         print("Successfully initialized Vertex AI")
#     except ImportError:
#         print("Vertex AI module not found. Skipping initialization.")
#     except Exception as e:
#         print(f"Error initializing Vertex AI: {e}")
    
#     # Initialize Gemini API if available
#     try:
#         if gemini_api_key:
#             import google.generativeai as genai
#             genai.configure(api_key=gemini_api_key)
#             print("Successfully initialized Gemini API")
#     except ImportError:
#         print("Google Generative AI module not found. Skipping initialization.")
#     except Exception as e:
#         print(f"Error initializing Gemini API: {e}")
    
#     return {
#         "vertexai": vertexai if 'vertexai' in locals() else None,
#         "project": project_id,
#         "location": vertex_location,
#         "api_key": gemini_api_key
#     }

# class CustomInvocationContext(InvocationContext):
#     """
#     A custom implementation of InvocationContext that satisfies all required attributes.
#     """
#     def __init__(self, input_text, customer_id, cloud_config=None):
#         self.input = input_text
#         self.customer_id = customer_id
#         self.vertexai = cloud_config.get("vertexai") if cloud_config else None
#         self.project = cloud_config.get("project") if cloud_config else None
#         self.location = cloud_config.get("location") if cloud_config else None
#         self.api_key = cloud_config.get("api_key") if cloud_config else None
        
#         # Include common attributes that might be needed for branching/flow control
#         self.branch = None
#         self.steps = []
#         self.history = []
#         self.data = {}
#         self.state = {}
#         self.errors = []
        
#     def model_copy(self, **kwargs):
#         """Required for Pydantic model compatibility"""
#         new_context = CustomInvocationContext(self.input, self.customer_id)
#         # Copy all attributes
#         for k, v in self.__dict__.items():
#             setattr(new_context, k, v)
#         # Apply any updates
#         for k, v in kwargs.items():
#             setattr(new_context, k, v)
#         return new_context

# async def run_aml_agent(customer_id=None):
#     """
#     Runs the AML monitoring agent with a specific customer ID.
    
#     Args:
#         customer_id (str, optional): The customer ID to analyze. If None, will use a default.
        
#     Returns:
#         Any: The result of the agent execution, or None if execution failed.
#     """
#     # Initialize Google Cloud services
#     cloud_config = initialize_google_cloud()
    
#     # Prepare the input for the root agent
#     if customer_id:
#         test_input = f"Analyze customer {customer_id} for suspicious activities and generate a comprehensive report."
#     else:
#         customer_id = "C10045"
#         test_input = f"Analyze customer {customer_id} for suspicious activities and generate a comprehensive report."

#     print(f"\nRunning AML agent with input: '{test_input}'")
#     print("\n" + "="*60)
#     print("STARTING ROOT AGENT PIPELINE")
#     print("="*60)

#     # Create the proper invocation context
#     context = CustomInvocationContext(test_input, customer_id, cloud_config)
    
#     # Run the agent
#     try:
#         results = []
#         print("\nExecuting agent with custom context...")
        
#         # Process async results
#         async for event in root_agent.run_async(context):
#             event_type = type(event).__name__
#             print(f"Received event: {event_type}")
            
#             # Store event details based on common event attributes
#             event_data = {}
#             if hasattr(event, "to_dict"):
#                 event_data = event.to_dict()
#             elif hasattr(event, "dict"):
#                 event_data = event.dict()
#             else:
#                 # Try to extract common attributes
#                 for attr in ["type", "message", "content", "data", "result"]:
#                     if hasattr(event, attr):
#                         event_data[attr] = getattr(event, attr)
            
#             results.append(event_data)
            
#             # Print detailed content for important events
#             if hasattr(event, "content") and event.content:
#                 print(f"Content: {event.content[:100]}...")
#             elif hasattr(event, "message") and event.message:
#                 print(f"Message: {event.message[:100]}...")
        
#         # Extract final result if available
#         final_result = None
#         if results:
#             # Try to find completion or final result event
#             for event in reversed(results):
#                 if event.get("type") in ["completion", "final", "result"]:
#                     final_result = event
#                     break
            
#             # If no specific final event found, use the last event
#             if not final_result:
#                 final_result = results[-1]
                
#         print("\nAnalysis completed successfully!")
#         return final_result
    
#     except Exception as e:
#         import traceback
#         print(f"Error executing agent: {e}")
#         traceback.print_exc()
#         return None

# if __name__ == "__main__":
#     import argparse
    
#     parser = argparse.ArgumentParser(description="Run AML monitoring agent")
#     parser.add_argument("--customer_id", help="Specify a customer ID to analyze")
    
#     args = parser.parse_args()
    
#     result = asyncio.run(run_aml_agent(args.customer_id))
    
#     print("\nAnalysis Result:")
#     print(json.dumps(result, indent=2) if result else "No results returned")
    
#     print("\n" + "="*60)
#     print("EXECUTION COMPLETED")
#     print("="*60)