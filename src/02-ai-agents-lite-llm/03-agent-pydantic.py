"""
03-agent-pydantic.py - Production-Ready AI Agents with Pydantic

This is an improved version of 02-agent.py that uses Pydantic for:
1. Type-safe tool definitions
2. Automatic JSON schema generation
3. Runtime validation
4. Better developer experience with autocomplete

The result: Cleaner code, fewer bugs, and better maintainability!
"""

from litellm import completion
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, Callable, Any, Type
import json

load_dotenv()


# =============================================================================
# Pydantic Models for Tool Definitions
# =============================================================================

class ToolParameter(BaseModel):
    """Base class for tool parameters - provides automatic JSON schema generation"""
    pass


class Tool(BaseModel):
    """
    Type-safe tool definition using Pydantic.

    Benefits:
    - Autocomplete in your IDE
    - Type checking
    - Automatic JSON schema generation
    - Clear, self-documenting code
    """
    name: str = Field(..., description="The name of the tool")
    description: str = Field(..., description="What the tool does")
    function: Callable = Field(..., description="The Python function to execute")
    parameters_model: Type[ToolParameter] = Field(..., description="Pydantic model for parameters")

    class Config:
        arbitrary_types_allowed = True  # Allow Callable type

    def to_litellm_tool(self) -> dict:
        """Convert to LiteLLM tool format with auto-generated schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_model.model_json_schema()
            }
        }

    def execute(self, arguments: dict) -> Any:
        """Execute the tool with validated parameters"""
        try:
            # Validate and parse arguments using Pydantic
            params = self.parameters_model(**arguments)

            # Execute with validated parameters
            result = self.function(**params.model_dump())
            return result
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"


# =============================================================================
# Improved Agent Class
# =============================================================================

class Agent:
    """
    Production-ready AI agent with Pydantic-powered tool definitions.

    Improvements over 02-agent.py:
    - Type-safe tool definitions
    - Automatic schema generation
    - Parameter validation
    - Cleaner tool registration
    - Better error handling
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        system_instruction: Optional[str] = None,
        tools: Optional[list[Tool]] = None,
        max_iterations: int = 10
    ):
        """
        Initialize the agent with Pydantic tools.

        Args:
            model: LiteLLM model name
            system_instruction: System prompt
            tools: List of Tool objects (Pydantic models)
            max_iterations: Maximum iterations for the agent loop
        """
        self.model = model
        self.system_instruction = system_instruction or "You are a helpful assistant."
        self.max_iterations = max_iterations

        # Store tools
        self.tools: dict[str, Tool] = {}
        self.tool_definitions: list[dict] = []

        if tools:
            for tool in tools:
                self.register_tool(tool)

        # Initialize conversation history
        self.messages = [{"role": "system", "content": self.system_instruction}]

    def register_tool(self, tool: Tool) -> None:
        """Register a Pydantic tool with the agent"""
        self.tools[tool.name] = tool
        self.tool_definitions.append(tool.to_litellm_tool())

    def run(self, prompt: str, verbose: bool = True) -> str:
        """
        Run the agent with a user prompt.

        Args:
            prompt: The user's input
            verbose: Whether to print debug information

        Returns:
            The agent's final response
        """
        # Add user message to history
        self.messages.append({"role": "user", "content": prompt})

        if verbose:
            print(f"\n{'='*70}")
            print(f"User: {prompt}")
            print(f"{'='*70}\n")

        # Run the agent loop
        for iteration in range(self.max_iterations):
            if verbose:
                print(f"[Iteration {iteration + 1}/{self.max_iterations}]")

            # Call the LLM
            response = completion(
                model=self.model,
                messages=self.messages,
                tools=self.tool_definitions if self.tool_definitions else None,
                tool_choice="auto" if self.tool_definitions else None
            )

            message = response.choices[0].message

            # Check if the model wants to call tools
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Add assistant's tool call to history
                self.messages.append(message.model_dump())

                if verbose:
                    print(f"🔧 Agent wants to call {len(message.tool_calls)} tool(s):\n")

                # Execute each tool call
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name

                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}

                    if verbose:
                        print(f"  📞 Calling: {tool_name}")
                        print(f"     Args: {tool_args}")

                    # Execute the tool using Pydantic validation
                    if tool_name in self.tools:
                        result = self.tools[tool_name].execute(tool_args)
                    else:
                        result = f"Error: Tool '{tool_name}' not found"

                    if verbose:
                        print(f"     ✓ Result: {result}\n")

                    # Add tool result to history
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": str(result)
                    })

                # Continue to next iteration
                continue

            # No tool calls - we have a final response
            final_response = message.content

            # Add to history
            self.messages.append({"role": "assistant", "content": final_response})

            if verbose:
                print(f"{'='*70}")
                print(f"🤖 Agent: {final_response}")
                print(f"{'='*70}\n")

            return final_response

        # Max iterations reached
        return "Error: Maximum iterations reached without final answer"

    def reset(self):
        """Reset conversation history"""
        self.messages = [{"role": "system", "content": self.system_instruction}]
        print("🔄 Conversation history reset\n")


# =============================================================================
# Example: Define Tools Using Pydantic
# =============================================================================

# Example 1: Weather Tool
class WeatherParams(ToolParameter):
    """Parameters for getting weather - with validation!"""
    location: str = Field(..., description="The city name (e.g., 'San Francisco', 'Tokyo')")


def get_weather(location: str) -> str:
    """Get the current weather for a location"""
    weather_data = {
        "san francisco": "☁️ Foggy, 58°F",
        "new york": "☀️ Sunny, 72°F",
        "london": "🌧️ Rainy, 55°F",
        "tokyo": "🌤️ Clear, 68°F",
        "paris": "☁️ Cloudy, 62°F"
    }
    result = weather_data.get(location.lower(), f"Weather data not available for {location}")
    return result


weather_tool = Tool(
    name="get_weather",
    description="Get the current weather for a city. Returns temperature and conditions.",
    function=get_weather,
    parameters_model=WeatherParams
)


# Example 2: Calculator Tool
class CalculatorParams(ToolParameter):
    """Parameters for calculator - type-safe math operations"""
    operation: str = Field(..., description="The operation: 'add', 'subtract', 'multiply', or 'divide'")
    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")


def calculator(operation: str, a: float, b: float) -> float | str:
    """Perform basic arithmetic operations"""
    ops = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }

    if operation not in ops:
        return f"Error: Unknown operation '{operation}'. Use: add, subtract, multiply, divide"

    result = ops[operation](a, b)
    return result


calculator_tool = Tool(
    name="calculator",
    description="Perform arithmetic operations (add, subtract, multiply, divide) on two numbers.",
    function=calculator,
    parameters_model=CalculatorParams
)


# Example 3: Search Tool (more complex parameters)
class SearchParams(ToolParameter):
    """Parameters for search with multiple fields"""
    query: str = Field(..., description="The search query")
    max_results: int = Field(default=5, description="Maximum number of results to return", ge=1, le=20)
    category: Optional[str] = Field(default=None, description="Optional category filter")


def search_database(query: str, max_results: int = 5, category: Optional[str] = None) -> str:
    """Search a mock database"""
    results = []
    for i in range(min(max_results, 3)):
        cat_str = f" in {category}" if category else ""
        results.append(f"Result {i+1}: {query}{cat_str}")

    return "\n".join(results)


search_tool = Tool(
    name="search_database",
    description="Search the database for relevant information. Can filter by category.",
    function=search_database,
    parameters_model=SearchParams
)


# =============================================================================
# Demo
# =============================================================================

def main():
    print("\n" + "="*70)
    print("🚀 Production-Ready AI Agent with Pydantic")
    print("="*70)

    # Create agent with our Pydantic tools
    agent = Agent(
        model="gpt-4o-mini",
        system_instruction="You are a helpful assistant with access to tools. Use them when needed.",
        tools=[weather_tool, calculator_tool, search_tool]
    )

    # Example 1: Using multiple tools
    print("\n📝 EXAMPLE 1: Multi-tool conversation")
    print("-" * 70)
    agent.run("What's the weather in Tokyo and Paris? Also calculate 144 divided by 12.")

    # Example 2: Complex query with optional parameters
    print("\n📝 EXAMPLE 2: Using optional parameters")
    print("-" * 70)
    agent.run("Search for 'Python tutorials' and give me 3 results in the 'programming' category")

    # Example 3: Following up (maintains context)
    print("\n📝 EXAMPLE 3: Context awareness")
    print("-" * 70)
    agent.run("What was the weather in Tokyo again?")

    # Example 4: Try with a different model
    print("\n📝 EXAMPLE 4: Same tools, different model")
    print("-" * 70)

    # Uncomment to try Claude (requires ANTHROPIC_API_KEY)
    # agent_claude = Agent(
    #     model="claude-3-5-sonnet-20241022",
    #     tools=[weather_tool, calculator_tool]
    # )
    # agent_claude.run("What's 25 times 4, and what's the weather in London?")

    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70)
    print("\nKey Benefits of Pydantic Approach:")
    print("  ✓ Type safety and autocomplete")
    print("  ✓ Automatic schema generation")
    print("  ✓ Runtime parameter validation")
    print("  ✓ Self-documenting code")
    print("  ✓ Easier to maintain and extend")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Required environment variables (add to .env file):
    # OPENAI_API_KEY=your_openai_key
    # ANTHROPIC_API_KEY=your_anthropic_key (optional)
    # GEMINI_API_KEY=your_gemini_key (optional)

    main()
