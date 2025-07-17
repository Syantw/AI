

import subprocess
import json
import threading
import queue
import time

class MCPProcessManager:
    """
    Manages the lifecycle and communication with the mobile-next-mcp process.
    """
    def __init__(self):
        self.mcp_process = None
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.stderr_thread = None
        self.stdout_thread = None
        self._stop_event = threading.Event()

    def start_mcp_process(self):
        """Starts the npx MCP server as a subprocess using the full path."""
        if self.mcp_process:
            print("MCP process is already running.")
            return

        try:
            self._stop_event.clear()
            command = "npx -y @mobilenext/mobile-mcp@latest"
            print(f"Starting MCP process with command: {command}")
            self.mcp_process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True
            )

            self.stdout_thread = threading.Thread(target=self._read_stdout)
            self.stderr_thread = threading.Thread(target=self._read_stderr)
            self.stdout_thread.daemon = True
            self.stderr_thread.daemon = True
            self.stdout_thread.start()
            self.stderr_thread.start()

            print("MCP process started successfully.")
            time.sleep(5)
            return True
        except Exception as e:
            print(f"Failed to start MCP process: {e}")
            self.mcp_process = None
            return False

    def _read_stdout(self):
        """Reads from the process's stdout until the stop event is set."""
        while not self._stop_event.is_set():
            try:
                line = self.mcp_process.stdout.readline()
                if line:
                    self.response_queue.put(line)
                else:
                    break
            except Exception:
                break

    def _read_stderr(self):
        """Reads from the process's stderr until the stop event is set."""
        while not self._stop_event.is_set():
            try:
                line = self.mcp_process.stderr.readline()
                if line:
                    print(f"[MCP Stderr] {line.strip()}")
                else:
                    break
            except Exception:
                break

    def send_command(self, command_dict):
        """Sends a JSON command to the MCP process."""
        if not self.mcp_process or self.mcp_process.poll() is not None:
            raise Exception("MCP process is not running.")

        try:
            command_json = json.dumps(command_dict)
            self.mcp_process.stdin.write(command_json + '\n')
            self.mcp_process.stdin.flush()

            response_line = self.response_queue.get(timeout=10)
            return json.loads(response_line)
        except queue.Empty:
            return {"status": "error", "message": "No response from MCP process."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def stop_mcp_process(self):
        """Stops the MCP process and associated threads gracefully."""
        if self.mcp_process:
            print("Stopping MCP process...")
            self._stop_event.set()
            self.mcp_process.terminate()
            try:
                self.mcp_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mcp_process.kill()
            
            self.mcp_process = None
            if self.stdout_thread.is_alive():
                self.stdout_thread.join(timeout=1)
            if self.stderr_thread.is_alive():
                self.stderr_thread.join(timeout=1)
            print("MCP process stopped.")

# Singleton instance
mcp_manager = MCPProcessManager()
