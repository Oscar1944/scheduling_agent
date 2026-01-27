# scheduling_agent
An agent to do scheduling &amp; email checking

# Overview


# Getting Start
To run scheduling agent, suggest to use ```python 3.13.10```.

- **Installation**  
      use the following command to install packages.  
      ``` pip install -r requirements.txt ```

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
   - ```agent_reasoning_log```: record status of whole agent reasoning process, including input message/routering/planning/tool-calling/observation/guardrail/final response.  

# Agent Architecture



# Prompting
