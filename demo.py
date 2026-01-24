from agent import Agent
import yaml

def main():

    return 0

if __name__=="__main__":
    with open("./config/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    LOG_PATH = "./logs/"

    agent = Agent(config["LLM"]["API_KEY"], config["LLM"]["MODEL"], LOG_PATH=LOG_PATH)

    # Demo: Easy Conversation
    # print("Demo: ", agent.chat('Hurry, tell Mike we gotta go now'))
    # print("Demo: ", agent.chat('How much is 10 multiply 20 ?'))
    # print("Demo: ", agent.chat('Please i want to know all of the events in schedule'))
    
    # [Pass] Demo check calendar

    # Demo Add new event
    mail = {
    "id": "EM011",
    "sender": "vendor@global_parts.com",
    "subject": "【年度結算】2/16(一) 早上線上對帳確認",
    "timestamp": "2026-01-19T19:00:00",
    "content": "您好，為了結算年度帳務，想跟您預約下個月 2/16（一）早上 10:00 進行年度對帳。需請您抽空參與，再請確認是否方便。"
    }
    new_event_conversation = "5月14號 Oscar 邀請我參加私人聚會，幫我記錄一下"
    print("Demo: ", agent.chat(str(mail)))
    print("Demo: ", agent.chat(str(new_event_conversation)))

    # Demo Delete an event
    mail = {
    "id": "EM011",
    "sender": "vendor@global_parts.com",
    "subject": "【年度結算】2/16(一) 早上線上對帳確認",
    "timestamp": "2026-01-21T19:00:00",
    "content": "您好，因財務系統突發狀況，下個月 2/16（一）早上 10:00 年度對帳會議取消"
    }
    # print("Demo: ", agent.chat(str(mail)))

    # Demo Revise an event
    mail = {
    "id": "EM011",
    "sender": "oscar@XXX.com",
    "subject": "Secret Party",
    "timestamp": "2026-01-23T19:00:00",
    "content": "Hey Sorry bro, bc some of them may have schedule conflict, i may change the meet to May 16. Is that ok for you ?"
    }
    revise_event_conversation = "幫我把 Test Event*UPdate* 改成 2/1 上午11:00"
    # print("Demo: ", agent.chat(str(mail)))
    # print("Demo: ", agent.chat(str(revise_event_conversation)))