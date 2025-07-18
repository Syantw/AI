from flask import Flask, request, jsonify
import requests
import os
from PIL import Image
from io import BytesIO
import json

app = Flask(__name__)

# Configuration
MCP_SERVER_URL = "http://localhost:8080"
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Default Ollama API URL
SCREENSHOTS_DIR = "screenshots"
OLLAMA_MODEL = "llama3" # Make sure this model is available in your Ollama instance

def get_ollama_actions(command: str) -> list:
    """
    Sends a command to Ollama to get a sequence of actions.
    """
    prompt = f"""
    You are an expert at controlling a mobile phone. Your task is to convert a natural language instruction into a sequence of precise actions that can be executed by a machine.
    The available actions are:
    - mobile_launch_app: Launches an app by package name
    - mobile_take_screenshot: Takes a screenshot of the current screen
    - mobile_click_on_screen_at_coordinates: Taps a specific coordinate on the screen
    - mobile_type_keys: Types the given text
    - mobile_swipe_on_screen: Swipes in a direction
    - mobile_press_button: Presses a device button (HOME, BACK, etc.)

    Instruction: "{command}"

    Based on the instruction, provide a JSON array of actions to be executed in sequence. For "mobile_click_on_screen_at_coordinates" actions, you must provide coordinates. For "mobile_type_keys" actions, you must provide the text. For "mobile_launch_app" actions, you must provide the package name.

    Example:
    Instruction: "Open WeChat and take a screenshot"
    Output:
    [
        {{"action": "mobile_launch_app", "params": {{"packageName": "com.tencent.mm"}}}},
        {{"action": "mobile_take_screenshot", "params": {{}}}}
    ]

    Now, generate the JSON for the instruction above.
    Output:
    """
    try:
        response = requests.post(OLLAMA_API_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        })
        response.raise_for_status()
        # The actual response from Ollama is a JSON string within a JSON object.
        response_json = json.loads(response.text)
        actions_str = response_json.get("response", "[]")
        return json.loads(actions_str)
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Ollama: {e}")
        print(f"Raw response: {response.text}")
        return []

def call_mcp_tool(tool_name: str, params: dict) -> dict:
    """
    Calls a mobile-mcp tool via MCP protocol
    """
    try:
        # MCP protocol format
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        print(f"Sending MCP request to {MCP_SERVER_URL}/mcp: {json.dumps(mcp_request, indent=2)}")
        
        # Increased timeout to 120 seconds for device operations
        response = requests.post(f"{MCP_SERVER_URL}/mcp", json=mcp_request, timeout=120)
        print(f"MCP response status: {response.status_code}")
        print(f"MCP response headers: {dict(response.headers)}")
        
        # Check if response is empty
        if not response.text.strip():
            print("Warning: Empty response from MCP server")
            return {"status": "success", "message": "Empty response but request sent"}
        
        # Try to parse JSON response
        try:
            response_json = response.json()
            print(f"MCP response JSON: {json.dumps(response_json, indent=2)}")
            return response_json
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Raw response text: {response.text}")
            # Return a structured response even if JSON parsing fails
            return {
                "status": "success", 
                "message": f"Request sent successfully, but response was not JSON: {response.text[:200]}"
            }
            
    except requests.exceptions.RequestException as e:
        print(f"Error calling MCP tool {tool_name}: {e}")
        raise e

@app.route('/execute', methods=['POST'])
def execute_command():
    """
    Receives a command from the cloud, gets actions from Ollama,
    and executes them on the mobile device.
    """
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"error": "Invalid request, 'command' not found"}), 400

    command = data['command']
    print(f"Received command: {command}")

    # Get actions from Ollama
    actions = get_ollama_actions(command)
    if not actions:
        return jsonify({"error": "Failed to get actions from Ollama or no actions returned."}), 500

    # 兼容 actions 是 dict 的情况
    if isinstance(actions, dict) and "actions" in actions:
        actions = actions.get("actions", [])

    print(f"Executing actions: {actions}")

    screenshot_paths = []
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)

    for i, action in enumerate(actions):
        action_name = action.get("action")
        params = action.get("params", {})
        print(f"Executing action {i+1}: {action_name} with params {params}")

        try:
            if action_name == 'mobile_take_screenshot':
                # Call MCP tool for screenshot
                result = call_mcp_tool("mobile_take_screenshot", {})
                print(f"Screenshot result: {result}")
                
                # Save screenshot if needed
                screenshot_path = os.path.join(SCREENSHOTS_DIR, f"step_{i}_{action_name}.png")
                # Note: MCP response format may vary, you might need to extract image data
                screenshot_paths.append(screenshot_path)

            elif action_name == 'mobile_launch_app':
                result = call_mcp_tool("mobile_launch_app", params)
                print(f"Launch app result: {result}")

            elif action_name == 'mobile_click_on_screen_at_coordinates':
                result = call_mcp_tool("mobile_click_on_screen_at_coordinates", params)
                print(f"Click result: {result}")

            elif action_name == 'mobile_type_keys':
                result = call_mcp_tool("mobile_type_keys", params)
                print(f"Type result: {result}")

            elif action_name == 'mobile_swipe_on_screen':
                result = call_mcp_tool("swipe_on_screen", params)
                print(f"Swipe result: {result}")

            elif action_name == 'mobile_press_button':
                result = call_mcp_tool("mobile_press_button", params)
                print(f"Press button result: {result}")

            else:
                print(f"Unknown action: {action_name}")

        except requests.exceptions.RequestException as e:
            error_message = f"Failed to execute action '{action_name}': {e}"
            print(error_message)
            return jsonify({"error": error_message, "screenshot_paths": screenshot_paths}), 500
        except Exception as e:
            error_message = f"An unexpected error occurred during action '{action_name}': {e}"
            print(error_message)
            return jsonify({"error": error_message, "screenshot_paths": screenshot_paths}), 500

    # Return success response
    if len(screenshot_paths) > 1:
        # Create a long image from multiple screenshots
        images = []
        for path in screenshot_paths:
            if os.path.exists(path):
                images.append(Image.open(path))
        
        if images:
            # Create a vertical concatenation of all screenshots
            total_height = sum(img.height for img in images)
            max_width = max(img.width for img in images)
            long_image = Image.new('RGB', (max_width, total_height))
            
            y_offset = 0
            for img in images:
                long_image.paste(img, (0, y_offset))
                y_offset += img.height
            
            long_image_path = os.path.join(SCREENSHOTS_DIR, "final_flow.png")
            long_image.save(long_image_path)
            return jsonify({"message": "Execution successful", "final_image": long_image_path, "actions_executed": actions})
    elif screenshot_paths:
        return jsonify({"message": "Execution successful", "final_image": screenshot_paths[0], "actions_executed": actions})
    else:
        return jsonify({"message": "Execution successful, no screenshots taken", "actions_executed": actions})


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "healthy", "message": "Agent server is running"})


if __name__ == '__main__':
    # Make sure you have a llama3 model in Ollama, otherwise change the model name
    # You can pull a model with `ollama pull llama3`
    app.run(debug=True, port=5000)