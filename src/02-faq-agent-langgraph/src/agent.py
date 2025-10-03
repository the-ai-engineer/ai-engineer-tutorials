import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from database import FAQDatabase

load_dotenv(override=True)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class FAQAgent:
    def __init__(self, database: FAQDatabase):
        self.database = database
        self.client = OpenAI()

        # Define the search tool
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_faqs",
                    "description": "Search the FAQ database for relevant information to answer user questions about policies and procedures",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find relevant FAQs",
                            }
                        },
                        "required": ["query"],
                    },
                },
            }
        ]

        self.system_message = {
            "role": "system",
            "content": (PROMPTS_DIR / "faq_agent.md").read_text().strip(),
        }

    def search_faqs(self, query: str) -> str:
        """Search the FAQ database and return formatted results"""
        results = self.database.search(query, top_k=3)
        if not results:
            return "No relevant FAQs found."

        formatted = []
        for result in results:
            formatted.append(f"{result['content']}")

        return "\n\n".join(formatted)

    def chat(self, message: str) -> str:
        """Send a message to the agent and get a response"""
        messages = [self.system_message, {"role": "user", "content": message}]

        # Tool-calling loop
        max_iterations = 5
        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                temperature=0,
            )

            message = response.choices[0].message

            # Add assistant message to history
            assistant_message = {"role": "assistant", "content": message.content}
            if message.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                        "type": "function",
                    }
                    for tc in message.tool_calls
                ]
            messages.append(assistant_message)

            # If no tool calls, we're done
            if not message.tool_calls:
                return message.content

            # Execute tool calls
            for tool_call in message.tool_calls:
                if tool_call.function.name == "search_faqs":
                    args = json.loads(tool_call.function.arguments)
                    result = self.search_faqs(args["query"])

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        }
                    )

        return "Maximum iterations reached."


def main():
    """Test the FAQ agent"""
    print("Loading FAQ database...")
    db = FAQDatabase()
    db.load_from_directory("documents")

    print("Initializing agent...")
    agent = FAQAgent(db)

    print("\nFAQ Agent ready! Type 'quit' to exit.\n")

    while True:
        question = input("You: ")
        if question.lower() in ["quit", "exit", "q"]:
            break

        response = agent.chat(question)
        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    main()
