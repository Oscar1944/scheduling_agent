from calendar import calendar
from fastmcp import FastMCP
from pathlib import Path
import json

# Create a server instance
mcp = FastMCP(name="MCPServer")

CALENDAR_FILE = Path("./data/calendar.json")

def load_calendar():
    if not CALENDAR_FILE.exists():
        return "Cannot find Calendar"
    with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_calendar(calendar: dict):
    with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
        json.dump(calendar, f, ensure_ascii=False, indent=4)

@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b

@mcp.tool()
def get_calendar_events():
    """
    Get event in schedule
    """
    return load_calendar()

@mcp.tool()
def add_calendar_event(event: dict):
    """
    Add events into schedule
    """
    calendar = get_calendar_events()
    calendar.append(event)
    save_calendar()

@mcp.tool()
def delete_calendar_event(event_id: str):
    """
    Delete events in schedule
    """
    calendar = get_calendar_events()
    calendar = [e for e in calendar if e["某條件"] != "某條件"]
    save_calendar()

if __name__=="__main__":
    # 啟動 server
    # mcp.run()
    mcp.run(transport="http", host="127.0.0.1", port=8000)