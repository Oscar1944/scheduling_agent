from agent import Agent
import yaml

def main():

    return 0

if __name__=="__main__":
    with open("./config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    agent = Agent(config["LLM"]["API_KEY"], config["LLM"]["MODEL"])
    print("Demo: ", agent.chat('Hurry, tell Mike we gotta go now'))
    print("Demo: ", agent.chat('How much is 10 multiply 20 ?'))