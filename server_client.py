import asyncio
import subprocess

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

FUNCTION_APP = "azure-function-jnb-agents"
MCP_URL = f"https://{FUNCTION_APP}.azurewebsites.net/runtime/webhooks/mcp"


def get_key() -> str:
    result = subprocess.run(
        ["az", "functionapp", "keys", "list",
         "--name", FUNCTION_APP,
         "--resource-group", "NovilloBenitoJaime",
         "--query", "systemKeys.mcp_extension",
         "--output", "tsv"],
        capture_output=True, text=True, check=True, shell=True,
    )
    return result.stdout.strip()


async def main() -> None:
    key = get_key()
    headers = {"x-functions-key": key}

    print(f"Connecting to {MCP_URL} ...")
    async with streamablehttp_client(MCP_URL, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Tools ({len(tools.tools)}):")
            for t in tools.tools:
                print(f"  {t.name} — {(t.description or '').splitlines()[0][:60]}")

            print("Escribe tu pregunta o 'quit'.\n")
            while True:
                try:
                    line = input("Tú: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not line or line in ("quit", "q", "salir"):
                    break
                result = await session.call_tool("LearnAgent", {"query": line})
                if not result.content:
                    print(f"[sin respuesta] isError={result.isError}\n")
                for item in result.content:
                    text = getattr(item, "text", None)
                    print(f"Agente: {text if text else repr(item)}\n")


if __name__ == "__main__":
    asyncio.run(main())
