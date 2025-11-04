"""
02-agent.py - Building AI Agents with LiteLLM

This demonstrates how to build a reusable AI agent that can:
1. Use tools/functions to interact with the world
2. Work with ANY AI model that supports tool calling
3. Maintain conversation history
4. Run autonomously until it has a final answer

The key insight: By using LiteLLM, our Agent class works with OpenAI, Anthropic,
Google, and 100+ other providers WITHOUT changing a single line of agent code!
"""

from litellm import completion
from dotenv import load_dotenv
from typing import Optional
import json
import subprocess
import os

load_dotenv()


class Agent:
    """
    A simple AI agent that uses LiteLLM for model-agnostic tool calling.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        system_instruction: Optional[str] = None,
        tools: Optional[list[dict]] = None,
        max_iterations: int = 10,
    ):
        self.model = model
        self.system_instruction = system_instruction or "You are a helpful assistant."
        self.max_iterations = max_iterations
        self.tools = tools or []

        # Initialize conversation history
        self.messages = [{"role": "system", "content": self.system_instruction}]

    def _get_tool_definitions(self) -> list[dict]:
        """Convert tools to LiteLLM format (OpenAI function calling schema)"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
            for tool in self.tools
        ]

    def _find_tool(self, tool_name: str) -> Optional[dict]:
        """Find a tool by name"""
        for tool in self.tools:
            if tool["name"] == tool_name:
                return tool
        return None

    def _execute_tool(self, tool_name: str, tool_args: dict) -> str:
        """Execute a tool and return its result"""
        tool = self._find_tool(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"

        # Check if approval is needed. If so, ask the user for approval.
        if tool.get("requires_approval", False):
            print("[APPROVAL REQUIRED]")
            print(f"Tool: {tool_name}")
            print(f"Args: {json.dumps(tool_args, indent=2)}")
            if input("\nApprove? (y/n): ").lower() not in ["y", "yes"]:
                return "Tool execution cancelled by user"

        try:
            return str(tool["function"](**tool_args))
        except Exception as e:
            return f"Error: {str(e)}"

    def run(self, prompt: str) -> str:
        """Run the agent with a user prompt"""
        self.messages.append({"role": "user", "content": prompt})

        tool_definitions = self._get_tool_definitions()

        for _ in range(self.max_iterations):
            # Call the LLM
            response = completion(
                model=self.model,
                messages=self.messages,
                tools=tool_definitions or None,
            )

            message = response.choices[0].message

            # If no tool calls, we're done
            if not hasattr(message, "tool_calls") or not message.tool_calls:
                self.messages.append({"role": "assistant", "content": message.content})
                return message.content

            # Add assistant's tool calls to history
            self.messages.append(message.model_dump())

            # Execute each tool
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Print what tool we're calling
                print(f"\n[TOOL CALL] {tool_name}({json.dumps(tool_args)})", flush=True)

                result = self._execute_tool(tool_name, tool_args)

                # Print result (truncate if too long)
                result_preview = result[:150] + "..." if len(result) > 150 else result
                print(f"[RESULT] {result_preview}\n", flush=True)

                # Add result to history
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": result,
                    }
                )

        return "Error: Maximum iterations reached"

    def reset(self):
        """Reset conversation history"""
        self.messages = [{"role": "system", "content": self.system_instruction}]


# ============================================================================
# Tool Functions
# ============================================================================


def bash_command(command: str) -> str:
    """Execute a bash command and return the output"""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        return output or "Command executed (no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


def read_file(filepath: str) -> str:
    """Read and return the contents of a file"""
    try:
        filepath = os.path.expanduser(filepath)

        if not os.path.isfile(filepath):
            return f"Error: File not found: {filepath}"

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        return content
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# Interactive Demo
# ============================================================================


def main():
    """Run an interactive chat loop with the agent"""

    tools = [
        {
            "name": "bash_command",
            "description": "Execute a bash command (e.g., 'ls -la', 'ps aux | grep python')",
            "function": bash_command,
            "requires_approval": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    }
                },
                "required": ["command"],
            },
        },
        {
            "name": "read_file",
            "description": "Read the contents of a text file",
            "function": read_file,
            "requires_approval": False,
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file"}
                },
                "required": ["filepath"],
            },
        },
    ]

    SYSTEM_PROMPT = """
    You are a system operations assistant on macOS with bash and file reading tools.

    Be concise and action-oriented:
    - State what you'll do, then do it
    - Format output as tables when showing structured data
    - Explain complex commands before running them
    - Prefer read-only operations
    - Never run destructive commands without confirmation

    Output markdown tables and code blocks for clarity."""

    agent = Agent(
        model="gpt-5",
        system_instruction=SYSTEM_PROMPT,
        tools=tools,
    )

    # Print header
    print("\n" + "=" * 70)
    print("AI AGENT WITH LITELLM")
    print("=" * 70)
    print(f"Model: {agent.model}")
    print("Commands: 'reset' to clear history, 'quit' to exit")
    print("=" * 70 + "\n")

    # Interactive loop
    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!\n")
                break

            if user_input.lower() == "reset":
                agent.reset()
                print("\n[Conversation reset]\n")
                continue

            # Run the agent
            print()
            response = agent.run(user_input)
            print(f"Agent: {response}\n")
            print("-" * 70 + "\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    main()
