
from agent_server import app

if __name__ == "__main__":
    print("=======================================")
    print("   Local Automation Agent")
    print("=======================================")
    print("-> Starting agent server using Flask's built-in server.")
    print("-> To start the MCP process, send a POST request to /start-mcp")
    print("-> To send a task, send a POST request to /execute with a JSON body like:")
    print("   { 'prompt': 'Your task for the mobile device...' }")
    print("-> To stop the MCP process, send a POST request to /stop-mcp")
    print("----------------------------------------")
    
    # Use Flask's own development server. It's simple and reliable.
    # The host='0.0.0.0' makes it accessible from the network.
    app.run(host="0.0.0.0", port=5001)
