# MCP Server — LearnAgent on Azure Functions

MCP (Model Context Protocol) server deployed on **Azure Functions** that exposes a `LearnAgent` tool: any MCP-compatible client (Claude Code, VS Code, custom agents) can call it to search and retrieve official **Microsoft Learn** documentation in real time.

Built with **Azure AI Foundry** as the LLM backend. Two components:

1. **`agent_client.py`** — local agent that queries Microsoft Learn docs via MCP
2. **`server/`** — MCP server deployed on Azure Functions, exposes a `LearnAgent` tool

---

## Consuming the deployed MCP server

**Endpoint:**
```
https://azure-function-jnb-agents.azurewebsites.net/runtime/webhooks/mcp
```

**Transport:** Streamable HTTP (MCP protocol 2025-03-26)

**Auth:** Azure Functions system key in header:
```
x-functions-key: <mcp_extension_key>
```

Get the key:
```bash
az functionapp keys list \
  --name azure-function-jnb-agents \
  --resource-group NovilloBenitoJaime \
  --query systemKeys.mcp_extension -o tsv
```

### Available tool

| Tool | Input | Description |
|------|-------|-------------|
| `LearnAgent` | `query` (string, required) | Searches and retrieves official Microsoft Learn documentation |

### Example — Python client

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import asyncio

KEY = "<mcp_extension_key>"
URL = "https://azure-function-jnb-agents.azurewebsites.net/runtime/webhooks/mcp"

async def main():
    async with streamablehttp_client(URL, headers={"x-functions-key": KEY}) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.call_tool("LearnAgent", {"query": "How to deploy Azure Container Apps?"})
            print(result.content[0].text)

asyncio.run(main())
```

Install: `pip install mcp`

### Example — VS Code / Claude Code (`mcp.json`)

```json
{
  "mcpServers": {
    "LearnAgent": {
      "url": "https://azure-function-jnb-agents.azurewebsites.net/runtime/webhooks/mcp",
      "headers": {
        "x-functions-key": "<mcp_extension_key>"
      }
    }
  }
}
```

### Example — curl (raw JSON-RPC)

```bash
KEY="<mcp_extension_key>"

# Initialize
curl -X POST https://azure-function-jnb-agents.azurewebsites.net/runtime/webhooks/mcp \
  -H "Content-Type: application/json" \
  -H "x-functions-key: $KEY" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# Call tool
curl -X POST https://azure-function-jnb-agents.azurewebsites.net/runtime/webhooks/mcp \
  -H "Content-Type: application/json" \
  -H "x-functions-key: $KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"LearnAgent","arguments":{"query":"Azure Blob Storage Python quickstart"}}}'
```

---

## Local agent (`agent_client.py`)

Connects to `https://learn.microsoft.com/api/mcp` directly and uses Azure AI Foundry as LLM.

**Requirements:** Python 3.9+, `az login`

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:
```env
FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
FOUNDRY_MODEL=gpt-4o-mini
```

```bash
python agent_client.py
```

---

## Deploying the server

```bash
cd server
# Edit requirements.txt if needed
Compress-Archive -Path function_app.py,host.json,requirements.txt -DestinationPath deploy.zip -Force
az functionapp deployment source config-zip \
  --name azure-function-jnb-agents \
  --resource-group NovilloBenitoJaime \
  --src deploy.zip --build-remote true
```

Required app settings on the Function App:
| Setting | Value |
|---------|-------|
| `FOUNDRY_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint |
| `FOUNDRY_MODEL` | Model deployment name |

The Function App needs **System Assigned Managed Identity** with **Azure AI Developer** role on the Foundry resource.

---

## Stack

| Component | Package |
|-----------|---------|
| MCP transport | `mcp>=1.9.0` |
| Agent orchestration | `agent-framework>=1.8.1` |
| Azure Functions hosting | `agent-framework-azurefunctions==1.0.0b260521` |
| Azure AI Foundry LLM | `agent-framework-foundry` |
| Azure auth | `azure-identity` |
