import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

transport = StreamableHttpTransport(url="http://127.0.0.1:8003/mcp")
client = Client(transport)

async def call_tool():
    async with client:
        res = await client.call_tool("movimientos_buscar_por_fechas", {
            "desde": "2025-11-10",
            "hasta": "2025-11-10"
        })
        print("movimientos_buscar_por_fechas:", res)
    

asyncio.run(call_tool())