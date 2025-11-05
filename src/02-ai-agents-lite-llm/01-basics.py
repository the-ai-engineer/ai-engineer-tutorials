"""
01-basics.py - Basic LiteLLM Usage

This demonstrates the fundamentals of using LiteLLM to call different AI models
with a unified interface. LiteLLM supports 100+ LLM providers including:
- OpenAI (gpt-4, gpt-3.5-turbo, etc.)
- Anthropic (claude-3-opus, claude-3-sonnet, etc.)
- Google (gemini-pro, gemini-flash, etc.)
- And many more!

Key concept: Same code works across all providers - just change the model name!
"""

from litellm import completion
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()


def basic_completion(model: str, prompt: str) -> str:
    """Make a basic completion call to any LLM via LiteLLM"""
    response = completion(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


response = basic_completion("gpt-5", "Do I need frameworks to build AI agents?")

basic_completion("gemini/gemini-2.5-flash", "HELLO")


def streaming_completion(model: str, prompt: str):
    """Stream responses token by token"""
    response = completion(
        model=model, messages=[{"role": "user", "content": prompt}], stream=True
    )

    print("Streaming response: ", end="", flush=True)
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print()  # New line at end
