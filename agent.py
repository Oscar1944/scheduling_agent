from util import guardrails
from util import LLM, getToday
from fastmcp.client import Client
import yaml
import ast
import asyncio

global prompt
with open("./prompts/prompt.yaml", "r", encoding="utf-8") as f:
    prompt = yaml.safe_load(f)

class Agent:
    def __init__(self, API_KEY, MODEL):
        self.memory = []
        self.llm = LLM(API_KEY, MODEL)
        self.objective = ""

    def chat(self, message):
        """
        Send message to Agent
        """
        today = getToday()
        tool_list = asyncio.run(self.list_tools())
        # print(tool_list)
        cur_status = []
        loop_cnt = 0
        max_loop = 3
        while loop_cnt<=max_loop:
            '''
            Planning -> Tool-calling -> LLM(continue/break)
            '''
            loop_cnt+=1
            sys_prompt = prompt["PLANNING"]["PROMPT_3"]
            instruction = sys_prompt.format(
                message=message,
                today_datetime=today, 
                cur_status=str(cur_status), 
                tool_list=str(tool_list)
            )
            res = self.llm.chat(instruction)
            print(res)

            if res:
                if "#Done#".lower() in res.lower():  # Planning Done
                    cur_status.append(res)
                    break
                else:
                    step = ast.literal_eval(res)
                    if "Action" in step.keys():   # Do Action
                        tool_result = asyncio.run(self.call_tool(step["Action"], param=step["param"]))
                        observation = str(f"[Observation] Calling {step['Action']} with param {step['param']}, Got result {tool_result}")
                        cur_status.append(observation)
                    elif "Thought" in step.keys():   # Thinking
                        cur_status.append(str(step["Thought"]))
                    else:
                        raise ValueError("LLM Planning Unknown step")
            else:
                raise ValueError("LLM respond None object")
            
            
            # Final Answer Generation
            final_sys_prompt = prompt["FINAL_ANS"]["PROMPT_TEST"]
            instruction = final_sys_prompt.format(
                message=message,
                today_datetime=today, 
                cur_status=str(cur_status)
            )
            res = self.llm.chat(instruction)

            ###
            ### Guardrails
            ###
            
            return res

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

    async def call_tool(self, tool, param=None):       
        """
        Call a tool and get response through MCP
        """
        async with Client("http://127.0.0.1:8000/mcp") as client:
            result = await client.call_tool("multiply", {"a":3, "b":4})
