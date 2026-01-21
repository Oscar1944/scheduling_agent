import asyncio
from fastmcp.client import Client

async def main():
    # 1️⃣ 使用 async context 連線 MCP Server
    async with Client("http://127.0.0.1:8000/mcp") as client:
        # 2️⃣ 呼叫工具
        result = await client.call_tool("multiply", {"a":3, "b":4})
        print("3 * 4 =", result)
        print(result.content[0].text)
        print("*********************")
        result = await client.call_tool("get_calendar_events")
        print(result.content[0].text) #str
# asyncio.run(main())

async def list_tools():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        tools = await client.list_tools()
        for tool in tools:
            print(tool)
asyncio.run(list_tools())
