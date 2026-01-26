from agent import Agent
import yaml
import json
from util import LLM, Guardrail

if __name__=="__main__":
    # Loading Email dataset
    with open("./emails.json", "r", encoding="utf-8") as f:
        emails = json.load(f)

    # Initialize Agent
    with open("./config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    with open("./prompts/safety_policy.yaml", "r", encoding="utf-8") as f:
        safety = yaml.safe_load(f)

    LOG_PATH = "./logs/"
    MAX_REASON = 15
    MAX_MEMO = len(emails)
    MAX_SAFETY_CORRECT = 5

    MODEL = LLM(config["LLM"]["API_KEY"], config["LLM"]["MODEL"])

    guardrail = Guardrail(
        POLICY=safety["GUARDRAIL"]["POLICY_1"], 
        CORRECT=safety["CORRECTION"], 
        MODEL=MODEL
        )
    agent = Agent(
        MODEL=MODEL, 
        LOG_PATH=LOG_PATH, 
        MAX_REASON=MAX_REASON, 
        MAX_MEMO=MAX_MEMO, 
        SAFETY=guardrail, 
        MAX_SAFETY_CORRECT=MAX_SAFETY_CORRECT
        )

    # Agent procesing Emails & Logged E2E response
    E2E_LOG_PATH = "./logs/E2E_log.txt"
    with open(E2E_LOG_PATH, 'w', encoding='utf-8') as f:
        print("Agent processing message ...")
        for id, email in enumerate(emails):
            res = agent.chat(str(email))
            f.write(f"==========<Email-{id}>===========\n")
            f.write(json.dumps(email, ensure_ascii =False, indent=4)+"\n")
            f.write("\n")
            f.write("[Agent Response] "+ res + "\n")
            f.write("==============<END>=============\n")

