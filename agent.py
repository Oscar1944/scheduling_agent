from util import LLM
from fastmcp.client import Client
import yaml

class Agent:
    def __init__(self):
        self.memory = []
        self.llm = LLM()

    def chat(self, message):
        """
        Send message to Agent
        """
        loop_cnt = 0
        max_loop = 3
        while True:
            '''
            Planning -> Tool-calling -> LLM(continue/break)
            '''
            cnt+=1
            prompt = "Prompt for planning"
            self.llm.chat(prompt, message)


    async def list_tools(self):
        """
        List details of all MCP tools
        Return (List[Dict]): tool_name, tool_description, tool_param
        """
        async with Client("http://127.0.0.1:8000/mcp") as client:
            tools = await client.list_tools()
            tool_detail = []
            for tool in tools:
                tool_detail.append({"Tool":tool.name, "Description":tool.description, "Parameters":tool.inputSchema["properties"]}) 

            return tool_detail               

