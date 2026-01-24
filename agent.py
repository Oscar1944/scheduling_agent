from util import guardrails
from util import LLM, getToday
from fastmcp.client import Client
import yaml
import ast
import asyncio
import os
import json

global prompt
with open("./prompts/prompt.yaml", "r", encoding="utf-8") as f:
    prompt = yaml.safe_load(f)

class Agent:
    def __init__(self, API_KEY, MODEL, LOG_PATH, MAX_MEMO=0):
        self.memory = []
        self.max_memory = MAX_MEMO
        self.llm = LLM(API_KEY, MODEL)
        self.log = LOG_PATH

        # Create an agent log
        if not os.path.exists(self.log):
            ValueError("Log path not exist.")
        else:
            self.log = os.path.join(self.log, 'agent_log.txt')
        with open(self.log, 'w', encoding='utf-8') as f:
            pass


    def chat(self, message):
        """
        Send message to Agent
        """
        _tag = "********* <thinking> *********"
        self._log(_tag)

        # Initialize
        reasoning_process = ""
        email_priority = ""
        today = getToday()

        # Router Scheeduling
        _tag = "<Logic Framework> Is about Events ?"
        self._log(_tag)
        sys_prompt = prompt["ROUTER"]["SCHEDULING"]["PROMPT_1"]
        router_res = self.router(sys_prompt, message)
        self._log(router_res)
        if router_res=='yes':
            _tag = "********* <planning> *********"
            self._log(_tag)
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
                res = self.llm.chat(instruction).strip().strip("'\"")
                self._log(res)

                if res:
                    if "#Done#".lower() in res.lower():  # Planning Done
                        cur_status.append(res)
                        break
                    else:
                        res = res.strip().splitlines()[0]
                        # step = ast.literal_eval(res)  # apply ast to convert str->dict
                        step = json.loads(res)  # apply json to convert str->dict
                        if "Action" in step.keys():   # Do Action
                            tool_result = asyncio.run(self.call_tool(step["Action"], param=step["param"]))
                            observation = str(f"[Observation] Calling {step['Action']} with param {step['param']}, Got result {tool_result}")
                            cur_status.append(observation)
                            self._log(observation)
                        elif "Thought" in step.keys():   # Thinking
                            cur_status.append(str(step["Thought"]))
                        else:
                            self._log("ValueError('LLM Planning Unknown step')")
                            raise ValueError("LLM Planning Unknown step")
                else:
                    self._log(res)
                    self._log("ValueError('LLM respond None object')")
                    raise ValueError("LLM respond None object")
            reasoning_process = "/n".join(cur_status)
        elif router_res=='no':
            # Not Scheduling processing
            pass
        else:
            self._log(router_res)
            self._log("ValueError('Unknown Scheduling Router Result')")
            raise ValueError("Unknown Scheduling Router Result")

            
        # Router IS_MAIL
        _tag = "<Logic Framework> Is Email ?"
        self._log(_tag)
        email_priority = None
        sys_prompt = prompt["ROUTER"]["IS_MAIL"]["PROMPT_1"]
        router_res = self.router(sys_prompt, message)
        self._log(router_res)
        if router_res=="yes":
            # Email process
            sys_prompt = prompt["EMAIL_PRIORITY"]["PROMPT_1"]
            instruction = sys_prompt.format(
                message=message
            )
            res = self.llm.chat(instruction).strip().strip("'\"")
            self._log(f"email priority: {res}")
            priority = ast.literal_eval(res)
            email_priority = f"Email_Type: {priority['Type']}, Score: {priority['Score']}"
        elif router_res=="no":
            # Not Email process
            pass
        else:
            self._log(router_res)
            self._log("ValueError('Unknown IS_MAIL Router Result')")
            raise ValueError("Unknown IS_MAIL Router Result")
        
        
        # Final Answer Generation
        _tag = "********* <Generate Response> *********"
        self._log(_tag)
        final_sys_prompt = prompt["FINAL_ANS"]["PROMPT_TEST"]
        instruction = final_sys_prompt.format(
            chat_history=json.dumps(self.memory, ensure_ascii=False, indent=4),
            today_datetime=today, 
            reasoning = reasoning_process,
            priority = email_priority,
            message=message
        )
        res = self.llm.chat(instruction)
        self._log(res)

        ###
        ### Guardrails
        ###

        # Add current response into chat history
        self._remember(message, res)
        
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

            return result.content[0].text

    def guardrail(self, message):
        """
        Dev
        """
        # sys_prompt = prompt["Guard1"]
        instruction = prompt.format(
            message=message
        )
        
        res = self.llm.chat(instruction)
        if res:
            print("Guardrail: ", res)
            return res.lower().strip().strip("'\"")
        else:
            return "LLM return None"
        
    def _log(self, msg):
        """
        Logged a message to record the process of an agent.
        Input (str): log message, the msg will be shown in terminal and recorded in log.
        Return : no return 
        """
        print(msg)
        with open(self.log, "a", encoding="utf-8") as log:
            print(msg, file=log)

    def _remember(self, message, response):
        """
        Add current final response into chat history as part of memory
        Return : no return 
        """
        cur_chat = [
            {"USER":message},
            {"Assistant": response}
        ]
        self.memory.append(cur_chat)

        if len(self.memory)>self.max_memory:
            self.memory.pop(0)





