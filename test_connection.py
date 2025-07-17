import requests
import time
import json
import uuid

def start_mcp():
    try:
        response = requests.post("http://localhost:5001/start-mcp")
        print("Start MCP response:", response.json())
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        print("Please make sure the main application is running.")

def test_list_devices_via_execute():
    try:
        prompt_data = {"prompt": "List all connected devices"}
        response = requests.post(
            "http://localhost:5001/execute",
            json=prompt_data
        )
        print("List Devices via /execute response:", response.json())
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    start_mcp()
    time.sleep(20) # Give MCP time to start
    test_list_devices_via_execute()