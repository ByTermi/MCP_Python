import asyncio

from azure.identity import AzureCliCredential
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from dotenv import load_dotenv

load_dotenv()

LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"


async def main() -> None:
    client = FoundryChatClient(credential=AzureCliCredential())

    async with Agent(
        client=client,
        name="LearnAgent",
        instructions=(
            "You are a Microsoft documentation assistant. "
            "Use your MCP tool to search and fetch official Microsoft Learn docs."
        ),
        tools=MCPStreamableHTTPTool(
            name="Microsoft Learn MCP",
            description="Access Microsoft Learn docs: search articles, fetch full pages, find code samples.",
            url=LEARN_MCP_URL,
        ),
    ) as agent:
        print("Microsoft Learn agent ready (Azure CLI auth). Type your question or 'quit'.\n")
        while True:
            try:
                query = input("User: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                break

            if not query:
                continue
            if query.lower() in ("quit", "exit", "q"):
                break

            result = await agent.run(query)
            print(f"Agent: {result.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
