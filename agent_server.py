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
    - tap(x, y): Taps a specific coordinate on the screen.
    - screenshot(): Takes a screenshot of the current screen.
    - type(text): Types the given text.
    - swipe(startX, startY, endX, endY, duration): Swipes from a start to an end coordinate.
    - sleep(ms): Waits for a specified number of milliseconds.

    Instruction: "{command}"

    Based on the instruction, provide a JSON array of actions to be executed in sequence. For "tap" actions, you must provide coordinates. For "type" actions, you must provide the text.

    Example:
    Instruction: "Open the settings and then take a screenshot."
    Output:
    [
        {{"action": "tap", "params": {{"x": 500, "y": 200}}}},
        {{"action": "screenshot", "params": {{}}}}
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
            if action_name == 'screenshot':
                res = requests.get(f"{MCP_SERVER_URL}/screenshot")
                res.raise_for_status()
                img = Image.open(BytesIO(res.content))
                screenshot_path = os.path.join(SCREENSHOTS_DIR, f"step_{i}_{action_name}.png")
                img.save(screenshot_path)
                screenshot_paths.append(screenshot_path)

            elif action_name == 'tap':
                res = requests.post(f"{MCP_SERVER_URL}/tap", json=params)
                res.raise_for_status()

            elif action_name == 'type':
                res = requests.post(f"{MCP_SERVER_URL}/type", json=params)
                res.raise_for_status()

            elif action_name == 'swipe':
                res = requests.post(f"{MCP_SERVER_URL}/swipe", json=params)
                res.raise_for_status()
            
            elif action_name == 'sleep':
                import time
                time.sleep(params.get('ms', 1000) / 1000)

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


    # Combine screenshots into a long image
    if len(screenshot_paths) > 1:
        images = [Image.open(p) for p in screenshot_paths]
        widths, heights = zip(*(i.size for i in images))

        total_height = sum(heights)
        max_width = max(widths)

        long_image = Image.new('RGB', (max_width, total_height))

        y_offset = 0
        for im in images:
            long_image.paste(im, (0, y_offset))
            y_offset += im.size[1]

        long_image_path = os.path.join(SCREENSHOTS_DIR, "final_flow.png")
        long_image.save(long_image_path)
        return jsonify({"message": "Execution successful", "final_image": long_image_path, "actions_executed": actions})
    elif screenshot_paths:
        return jsonify({"message": "Execution successful", "final_image": screenshot_paths[0], "actions_executed": actions})
    else:
        return jsonify({"message": "Execution successful, no screenshots taken", "actions_executed": actions})


if __name__ == '__main__':
    # Make sure you have a llama3 model in Ollama, otherwise change the model name
    # You can pull a model with `ollama pull llama3`
    app.run(debug=True, port=5000)