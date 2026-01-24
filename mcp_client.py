import asyncio
from fastmcp.client import Client

async def main():
    # 1️⃣ 使用 async context 連線 MCP Server
    async with Client("http://127.0.0.1:8000/mcp") as client:
        # 2️⃣ 呼叫工具
        # result = await client.call_tool("multiply", {"a":3, "b":4})
        # print("3 * 4 =", result)
        # print(result.content[0].text)
        # print("*********************")
        result = await client.call_tool("get_calendar_events")
        print(result.content[0].text) # str
# asyncio.run(main())
print("*************")

async def list_tools():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        tools = await client.list_tools()
        for tool in tools:
            print(tool)
# asyncio.run(list_tools())
print("*************")

test_event = {"event":{"title": "Test Event===", "start":"2030-01-20", "end":"2030-2-30"}}
async def add_calendar_event(test_event):
    async with Client("http://127.0.0.1:8000/mcp") as client:
        res = await client.call_tool("add_calendar_event", test_event)
        print(res)
asyncio.run(add_calendar_event(test_event))
print("*************")



test_event = {"event":{"title": "Test Event***", "start":"2030-01-50", "end":"2030-2-30"}}
async def add_calendar_event(test_event):
    async with Client("http://127.0.0.1:8000/mcp") as client:
        res = await client.call_tool("add_calendar_event", test_event)
        print(res)
asyncio.run(add_calendar_event(test_event))
print("*************")



target_date = {"datetime":"2030-01-20"}
async def delete_calendar_event(target_date):
    async with Client("http://127.0.0.1:8000/mcp") as client:
        res = await client.call_tool("delete_calendar_event", target_date)
        print(res)
asyncio.run(delete_calendar_event(target_date))
print("*************")



target_event = {"title": "Test Event***", "start":"2030-01-50", "end":"2030-2-30"}
revised_event = {"title": "Test Event*UPdate*", "start":"2030-01-50", "end":"2030-2-30"}
update = {"event":target_event, "revised_event":revised_event}
async def revise_calendar_event(update):
    async with Client("http://127.0.0.1:8000/mcp") as client:
        res = await client.call_tool("revise_calendar_event", update)
        print(res)
asyncio.run(revise_calendar_event(update))
print("*************")
