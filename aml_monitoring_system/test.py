import requests
import json
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Input: app_name, user_id, session_id
app_name = input("Enter the app_name: ")
user_id = input("Enter the user_id: ")
session_id = input("Enter the session_id: ")

# Define the API endpoint with dynamic values
url = f"https://amlagent-1013958054897.us-central1.run.app/apps/{app_name}/users/{user_id}/sessions/{session_id}"

# Define headers
headers = {
    "Content-Type": "application/json"
}

# Define the body of the request to create a session
body = {
"additionalProp1": {}
}

# Send a POST request to create the session
response = requests.post(url, headers=headers, data=json.dumps(body), verify=False)

# Check the response status and content
if response.status_code == 200:
    print("Session created successfully!")
    print(response.json())  # You can check the API response here
else:
    print(f"Failed to create session: {response.status_code}, {response.text}")

message = "C10045"

data = {
    "app_name": app_name,
    "user_id": user_id,
    "session_id": session_id,
    "new_message": {
        "role": "user",
        "parts": [{
            "text": message
        }]
    },
    "streaming": False
}

#response = requests.post(f"{"https://crashai-agentapi-700469397525.us-central1.run.app/"}/run", headers=headers, data=json.dumps(data),verify=False)
response = requests.post("https://amlagent-1013958054897.us-central1.run.app/run", headers=headers, data=json.dumps(data), verify=False)

# Handle the response
if response.status_code == 200:
    print("Message sent successfully!")
    print(response.json())  # Print the API response
else:
    print(f"Failed to send message: {response.status_code}, {response.text}")
 