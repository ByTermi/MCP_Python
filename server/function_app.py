import os

from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.azure import AgentFunctionApp
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

client = FoundryChatClient(credential=DefaultAzureCredential())

agent = Agent(
    client=client,
    name="LearnAgent",
    instructions="You are a Microsoft documentation assistant. Use your MCP tool to search and fetch official Microsoft Learn docs.",
    description="Search and retrieve official Microsoft Learn documentation.",
    tools=MCPStreamableHTTPTool(
        name="Microsoft Learn MCP",
        description="Access Microsoft Learn docs: search articles, fetch full pages, find code samples.",
        url="https://learn.microsoft.com/api/mcp",
    ),
)

app = AgentFunctionApp(enable_health_check=True)
app.add_agent(agent, enable_http_endpoint=True, enable_mcp_tool_trigger=True)
