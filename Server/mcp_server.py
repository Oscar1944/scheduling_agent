from fastmcp import FastMCP
from pathlib import Path
import json
import requests
from datetime import datetime


# Create a server instance
mcp = FastMCP(name="MCPServer")

CALENDAR_FILE = Path(__file__).resolve().parent.parent / "data" / "calendar.json"

def load_calendar():
    """
    Load calendar.json as a dict
    Return (dict): calendar obj
    """
    if not CALENDAR_FILE.exists():
        return "Cannot find Calendar"
    with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_calendar(calendar: dict):
    """
    Re-write & Save canlendar.json
    Return: None
    """
    with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
        json.dump(calendar, f, ensure_ascii=False, indent=4)

@mcp.tool
def multiply(a: float, b: float) -> float:
    """
    Multiplies two numbers by giving 2 real numbers a and b.
    Input: a, b are numbers
    Return (float): the product of multiplication
    """
    return a * b

@mcp.tool()
def get_calendar_events():
    """
    Get all of events & date that have been scheduled in calendar.
    Input: No Input
    Return (str): All of Events in Calendar formated in JSON
    """
    return json.dumps(load_calendar(), ensure_ascii=False, indent=4)

@mcp.tool()
def add_calendar_event(event: dict):
    """
    Add a new events into calendar.
    Input: event (dict), an event should includ keys 'title', 'start', 'end'
    Return (str): A string to reply it is done.
    """
    calendar = load_calendar()  # list[dict]
    norm_event = {k.lower(): v for k, v in event.items()}

    # Check necessary content in an event
    event_keys = set(k for k in norm_event.keys())
    if "title" not in event_keys:
        return "Cannot find 'title' in event"
    if "start" not in event_keys:
        return "Cannot find 'start' in event"
    if "end" not in event_keys:
        return "Cannot find 'end' in event"
    
    calendar.append(norm_event)
    save_calendar(calendar)

    return "[Success] Add NEW EVENT"

@mcp.tool()
def delete_calendar_event(datetime: str):
    """
    Delete an events in calendar by giving a string datetime with format 'YYYY-MM-DD'.
    Input: event (dict), a string of datetime in format 'YYYY-MM-DD'
    Return (str): A string to reply it is done.
    """
    #
    # Need an time format alignment logic 
    #
    calendar = load_calendar()  # list[dict]
    deleted_event = [e for e in calendar if e["start"][:10]==datetime]

    if not deleted_event:
        return "Cannot find target event in calendar"
    else:
        calendar = [e for e in calendar if e["start"][:10]!=datetime]
    save_calendar(calendar)

    return "[Success] Delete an EVENT"

@mcp.tool()
def revise_calendar_event(event: dict, revised_event: dict):
    """
    Revise an events in calendar by giving a modified event.
    Input: 
        - event (dict), the original event that need to be modified, it should includ keys 'title', 'start', 'end'.
        - modified event (dict), a modified event, it should includ keys 'title', 'start', 'end'
    Return (str): A string to reply it is done.
    """
    calendar = load_calendar()  # list[dict]
    norm_event = {k.lower(): v for k, v in event.items()}
    norm_revised_event = {k.lower(): v for k, v in revised_event.items()}

    # Check necessary content in an original event
    if "start" not in norm_event.keys():
        return "Cannot find 'start' in original event"
    
    # Check necessary content in an revised event
    revised_event_keys = set(k.lower() for k in norm_revised_event.keys())
    if "title" not in revised_event_keys:
        return "Cannot find 'title' in revised event"
    if "start" not in revised_event_keys:
        return "Cannot find 'start' in revised event"
    if "end" not in revised_event_keys:
        return "Cannot find 'end' in revised event"
    
    # Replace original event with a new one
    for id, e in enumerate(calendar):
        if e["start"][:10]==event["start"][:10]:
            calendar[id]=norm_revised_event
            break
    
    save_calendar(calendar)

    return "[Success] Revise an EVENT" 

@mcp.tool()
def is_date_available(date: str):
    """
    Check if the given date is a holiday, weekend or weekday. The given datetime should be with format 'YYYY-MM-DD'.
    Input: date (str), a string of datetime in format 'YYYY-MM-DD'
    Return (str): A string to reply it is 'Holiday', 'Weekend' or 'Weekday'.
    """
    # API provided by government of new taipei city (https://data.ntpc.gov.tw/openapi)
    base_url = "https://data.ntpc.gov.tw/api/datasets/308dcd75-6434-45bc-a95f-584da4fed251/json?page={page_num}&size={size}"
    page_num = 10
    size = 100

    # Normalize datetime format
    target_dt = datetime.strptime(date, "%Y-%m-%d")  # convert str->datetime obj

    while True:
        url = base_url.format(page_num=page_num, size=size)
        holidays = requests.get(url, verify=False).json()   # List[dict], all holidays from new_taipei .gov web
        for holiday in holidays:
            _dt = datetime.strptime(holiday["date"], "%Y%m%d")  # convert str->datetime obj
            if _dt < target_dt:
                continue
            elif _dt > target_dt:
                # Cannot find the given date in all holidays
                return f"{date} is a normal Weekday."
            else:
                # Find the given date in all holidays
                return f"{date} is {holiday["holidaycategory"]}, Festival: {holiday["name"]}, Description: {holiday["description"]}."
        
        # If target date not in holidays list, keep checking next page.
        page_num+=1


        

if __name__=="__main__":
    # 啟動 server
    # mcp.run()
    mcp.run(transport="http", host="127.0.0.1", port=8000)

    # Dev-test
    # res = get_calendar_events()
    # print(res)

    # test_event = {"title": "Test Event-1", "start":"2030-01-20", "end":"2030-02-30"}
    # res = add_calendar_event(test_event)
    # print(res)
    # print("***********")
    # test_event = {"title": "Test Event-2", "start":"2030-05-17", "end":"2030-06-30"}
    # res = add_calendar_event(test_event)
    # print(res)
    # print("***********")


    # delete_event = "2030-01-20"
    # res = delete_calendar_event(delete_event)
    # print(res)
    # print("***********")

    # target_event = {"title": "Test Event-2", "start":"2030-05-17", "end":"2030-06-30"}
    # revised_event = {"title": "Test Event-Update", "start":"2030-0XX-17", "end":"2030-06-30"}
    # res = revise_calendar_event(target_event, revised_event)
    # print(res)

    # date = "2026-05-16" # weekday
    # date = "2026-02-16" # Holiday
    # date = "2026-02-22" # Weekend
    # res = is_date_available(date)
    # print(res)
    