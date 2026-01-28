# Scheduling_agent
An agent for scheduling &amp; email processing
1. 每一封信的郵件分類、優先評級 (1~5)、信件回覆內容，請參考 ``` /logs/E2E_log (demo).txt ```
2. 更新後的 calendar.json ，請參考 ``` /data/calendar (demo).json ```
3. 說明如何啟動程式 & MCP Server，請參考README ```Getting Started```
4. 演示 Agent 處理 13 封測試郵件的過程，並展現其在面對日期陷阱(國定假日) 時的決策流程，請參考 ``` /logs/agent_reasoning_log (demo).txt ```
5. 說明如何處理「除夕與週末」的推理判斷邏輯，請參考README ```Overview/Design/External Knowledge (周末/除夕)```
6. 說明設計 Prompt 或 Workflows 來避免模型幻覺，請參考README ```Overview/Design```
---

# Getting Started
To run scheduling agent, suggest using ```python 3.13.10```.

- **Installation**  
    -  Use the following command to install packages.  
      ``` pip install -r requirements.txt ```
    -  To use virtual environment, please refer to the following command  
      ``` cd scheduling_agent ```  
      ``` source dev-env/Scripts/activate ```

- **Run MCP Server**  
      Running on local ```127.0.0.1:8000/mcp```  
      ``` python Server/mcp_server.py ```

- **Setting LLM Services**  
      Scheduling Agent applies Gemini as core LLM.  Please refer to [AI Studio](https://aistudio.google.com/) to get Gemini API key.  
      [AI Studio](https://aistudio.google.com/) provides free API key with limited tokens and billing API, please make sure your API Key is available and tokens are enough for running agent.  
      When having Gemini API key, input API key and model name in ```config/config.yaml```, ```gemini-2.5-flash``` is suggested.

- **Run Agent**  
   Activate agent to process emails.  
   ```python run_agent.py```

- **Logging**  
   The Agent Response and Reasoning process will be logged and saved at ```./logs/```(default).  
   - ```E2E_log.txt```: record only input message and agent End-to-End response.  
   - ```agent_reasoning_log.txt```: record the status of entire agent reasoning process, including input message/routering/planning/tool-calling/observation/guardrail/final response.  

# Overview  

## Objective

- The scheduling agent aims to help user process daily emails and handle event arrangement.  
- The agent will prioritize each of email by the content of email.

## Agent Architecture

### Input
- Emails 
- Assume USER may also input daily conversations.

### Structure

![image](./png/agent_architecture.png)

<details>
<summary> Schedule_Router </summary>
A router LLM to decide if the given content (email or conversation) is about scheduling an event.
  - **If 'YES'**, agent starts reasoning to deal with event arrangement.
  - **If 'No'**, agent skips reasoning process.
</details>

<details>
<summary> Reasoning </summary>
It is a process of ReAct pattern (Thought->Action->Observation) allowing agent to think and call necessary tools based on the given content and objective.

**(1) Planning**
- Agent generates *thought* and *Action* based on current status.

**(2) Tool-Calling**
- Agent calls tools through MCP with parameters generated from previous planning step.

**(3) Observation**
- It is the result after calling a MCP tool.  
- The observation will be recorded so that the next round of reasoning will generate output based on the updated current status.
</details>

<details>
<summary> Mail_Router </summary>
A router LLM to decide if the given content is an email.
  - **If 'Yes'**, agent start prioritizing the given email by classifying types of email and scoring the email from 1 to 5.  
  - **If 'No'**, agent skip prioritizing process.
</details>

<details>
<summary> Email_Prioritize </summary>
Define types of email, and score email from 1 to 5 based on the given content.
  - **Type**: 急件, 一般, 詢價, 會議邀約, 垃圾  
  - **Score**: 1 to 5 (from low to high priority)
</details>

<details>
<summary> Final Answer Generation </summary>
This is a step to generate agent final response by referring all of previous results  
  (reasoning, chat_history, message).
</details>

<details>
<summary> Guardrail </summary>

**(1) Safety_Judge**
-  The final response will be given, and a LLM will be applied to judge and check if the given content violates safety policies.
  - **If 'Yes'**, Safety_Judge should provide brief explanation and suggestion.  
  - **If 'No'**, The final response will be shown as agent replies.

**(2) Re-writer**
- The final response and judge feedback will be given.
- It's supposed to re-write the given content based on feedback and send the output to Safety_Judge again.
</details>



## Design
To avoid the hallucination of LLM and guide agent to generate expected output, the design focus on the following aspects.

### Logic Framework

In this case, ***Routing*** pattern has been applied to structure the workflow. This will narrow down and simplify sub-process for LLM by separating **what should do** and **What to do**, helping LLM to process task with **single responsibility** instead of processing all tasks at a time and increase probability of hallucination.

The ***scheduling_agent*** applied 2 router LLMs to define logic framework. Ex: *Schedule_router* define the given message if it is about scheduling an event (Add/Delete/Modify/Check). If so, the agent would run into *"Reasoning"* sub-process, otherwise, the agent could avoid unnecessary token consumption.

### Reasoning Framework

This define a framework for agent to think **What to do** to complete tasks. ***ReAct*** (Reason-Action) pattern has been applied in reasoning framework. An LLM would be asked to think what to do next based on the current status. In this framework, LLM will go through a ***planning>>tool-calling>>observation*** looping process to figure out current status and which MCP tools should be called.

Instead of figuring out what to do in one step, ReAct reasoning process help agent to think step-by-step based on current status and reduce hallucination caused by LLM while processing a complex problem at a time.

### Prompting

Each of LLM in *scheduling_agent* would be instructed by giving narrow, structured prompts and required formats to harness the output of LLM and avoid hallucination.

Additionaly, dynamic information would be embedded in prompt as critical information to provide true reference for LLM based on different functions. 

Example: 
- A clear description of task , responsibility, MCP tools and past reasoning status will be provided to reasoning LLM as true references and avoid hallucination.
- Reasoning status, Email message is provided to Final-Answer LLM to generate expected response.   

### External Knowledge (周末/除夕)

To avoid hallucination during the process over reasoning event dates for an event, the reliable reference for dates should be provided as external source of truth. 

In this case, the holiday information is acquired through open API provided by ***the government of New Taipei City*** [open data portal](https://data.ntpc.gov.tw/openapi) as external data source. Checking holiday through this API is wrapped as an MCP tool, and agent is able to use this tool as needed to check if a specific date is a holiday during reasoning process. 

Ex: The agent would use an MCP tool ***is_date_available()*** to check whether a date is a holiday. If it is a holiday, the agent should think of another candidate date and check availability again during the ***Reasoning*** process.

### Guardrail Framework

In guardrail, ***Self-Reflection*** pattern has been applied. A brief explanation and suggestion would be provided by *safety_judge* when it detect a violation of safety policies. Afterwards, *re-writer* should revise content of final response depending on the feedback from *safety_judge*. This mechanism provide a guideline to *re-writer* and mitigate hallucination that could be generated.  
























