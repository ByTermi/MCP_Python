# MCP_Python

Python agent that connects to the **Microsoft Learn MCP server** using the [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) and authenticates via **Azure CLI** (`az login`).

## What it does

- Connects to `https://learn.microsoft.com/api/mcp` (Streamable HTTP transport, no API key needed)
- Uses **Azure AI Foundry** as the LLM backend (`gpt-4o-mini`)
- Authenticates with `AzureCliCredential` — no secrets in code
- Interactive REPL: ask questions, agent searches/fetches official Microsoft docs and answers

## Available MCP tools (exposed by Microsoft Learn)

| Tool | Description |
|------|-------------|
| `microsoft_docs_search` | Search official Microsoft/Azure docs, returns up to 10 chunks |
| `microsoft_code_sample_search` | Search code examples from Microsoft Learn |
| `microsoft_docs_fetch` | Fetch a full docs page as markdown from a URL |

## Requirements

- Python 3.9+
- Azure CLI logged in (`az login`)
- Azure AI Foundry project with a `gpt-4o-mini` deployment

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create `.env` in the project root:

```env
FOUNDRY_PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>
FOUNDRY_MODEL=gpt-4o-mini
```

## Run

```bash
az login                     # once — credentials cached
python agent_client.py
```

```
Microsoft Learn agent ready (Azure CLI auth). Type your question or 'quit'.

User: How do I deploy a container to Azure Container Apps?
Agent: ...
```

## Stack

| Component | Package |
|-----------|---------|
| MCP client | `mcp>=1.9.0` |
| Agent orchestration | `agent-framework>=1.8.1` |
| Azure AI Foundry LLM | `agent-framework-foundry` (bundled) |
| Azure auth | `azure-identity` |
| Env vars | `python-dotenv` |
