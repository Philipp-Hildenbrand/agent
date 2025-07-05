import json, subprocess

# -- Configuration --
FORBIDDEN_COMMANDS = json.load(open("config.json", "r"))["FORBIDDEN_COMMANDS"]
AGENT_BASE_DIR = json.load(open("config.json", "r"))["AGENT_BASE_DIR"]

# -- Shell Executor Prompt --
SHELL_EXECUTOR_PROMPT = """
**Shell Executor**: Execute system shell commands. Use this tool to interact with the underlying system, install packages, or run scripts. Do not use it for tasks that involve generating or processing information that you can handle internally.
    * **Usage**: `<<<SHELL:'command_to_execute'>>>`
    * **Example**: `<<<SHELL:'python -c "print("Hello World!")"'>>>`, `<<<SHELL:'pip install requests'>>>`. Don't add extra quotes.
"""

# -- Shell Executor Class --
class ShellExecutor:
    # Execute Shell Command
    def execute(self, command: str="", timeout: int=300) -> str:
        try:
            if command.startswith('killall'):
                command = """pids=$(pgrep -f 'program_name.*<AGENT_BASE_DIR>'); if [ -n "$pids" ]; then kill $pids; echo "Killed processes with PIDs: $pids"; else echo "No matching processes found in sandbox."; fi"""
            if any(command.strip().startswith(forbidden) for forbidden in FORBIDDEN_COMMANDS):
                return "Error: Forbidden shell command detected."
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                check=False, cwd=AGENT_BASE_DIR, timeout=timeout
            )
            stdout = f"STDOUT:\n{result.stdout.strip()}" if result.stdout else "STDOUT: [empty]"
            stderr = f"STDERR:\n{result.stderr.strip()}" if result.stderr else "STDERR: [empty]"
            return f"{stdout}\n{stderr}"
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds."
        except Exception as e:
            return f"Error executing shell command: {e}"