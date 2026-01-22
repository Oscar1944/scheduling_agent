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
        print("********* <thinking> *********")
        # Information
        reasoning_process = ""
        email_priprity = ""
        today = getToday()

        # Router Scheeduling
        print("<Logic Framework> Is about Events ?")
        sys_prompt = prompt["ROUTER"]["SCHEDULING"]["PROMPT_1"]
        router_res = self.router(sys_prompt, message)
        if router_res=='yes':
            print("********* <planning> *********")
            # Scheduling process
            tool_list = asyncio.run(self.list_tools())
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
                # print(instruction)
                res = self.llm.chat(instruction)
                print(res)

                if res:
                    if "#Done#".lower() in res.lower():  # Planning Done
                        cur_status.append(res)
                        break
                    else:
                        res = res.strip().splitlines()[-1]
                        step = ast.literal_eval(res)
                        if "Action" in step.keys():   # Do Action
                            tool_result = asyncio.run(self.call_tool(step["Action"], param=step["param"]))
                            observation = str(f"[Observation] Calling {step['Action']} with param {step['param']}, Got result {tool_result}")
                            cur_status.append(observation)
                            print(observation)
                        elif "Thought" in step.keys():   # Thinking
                            cur_status.append(str(step["Thought"]))
                            print(str(step["Thought"]))
                        else:
                            raise ValueError("LLM Planning Unknown step")
                else:
                    print(res)
                    raise ValueError("LLM respond None object")
            reasoning_process = "/n".join(cur_status)
        elif router_res=='no':
            # Not Scheduling processing
            pass
        else:
            print(router_res)
            raise ValueError("Unknown Scheduling Router Result")

            
        # Router IS_MAIL
        print("<Logic Framework> Is Email ?")
        sys_prompt = prompt["ROUTER"]["IS_MAIL"]["PROMPT_1"]
        router_res = self.router(sys_prompt, message)
        if router_res=="yes":
            # Email process
            sys_prompt = prompt["EMAIL_PRIORITY"]["PROMPT_1"]
            instruction = sys_prompt.format(
                message=message
            )
            res = self.llm.chat(instruction)
            priority = ast.literal_eval(res)
            email_priprity = f"Email_Type: {priority['Type']}, Score: {priority['Score']}"
        elif router_res=="no":
            # Not Email process
            pass
        else:
            print(router_res)
            raise ValueError("Unknown IS_MAIL Router Result")
        
        
        # Final Answer Generation
        print("********* <Generate Response> *********")
        final_sys_prompt = prompt["FINAL_ANS"]["PROMPT_TEST"]
        instruction = final_sys_prompt.format(
            today_datetime=today, 
            reasoning = reasoning_process,
            priority = email_priprity,
            message=message
        )
        res = self.llm.chat(instruction)

        ###
        ### Guardrails
        ###
        
        return res

    def router(self, prompt, message):
        """
        A router (LLM) to define the intent of USER by given a message.
        Return (str): Intent
        """
        # sys_prompt = prompt["ROUTER"]["PROMPT_1"]
        instruction = prompt.format(
            message=message
        )
        
        res = self.llm.chat(instruction)
        if res:
            print("Router: ", res)
            return res.lower().strip().strip("'\"")
        else:
            return "LLM return None"


    async def list_tools(self):
        """
        List details of all MCP tools
        Return (List[Dict]): tool_name, tool_description, tool_param
        """
        async with Client("http://127.0.0.1:8000/mcp") as client:
            tools = await client.list_tools()
            all_tool_detail = ""
            for tool in tools:
                tool_detail = f"('Tool':{tool.name}, 'Description': {tool.description}, 'Parameters': {tool.inputSchema['properties']})"
                all_tool_detail = all_tool_detail + tool_detail + "/n"

            return all_tool_detail        

    async def call_tool(self, tool, param=None):       
        """
        Call a tool and get response through MCP
        """
        async with Client("http://127.0.0.1:8000/mcp") as client:
            result = await client.call_tool(tool, param)

