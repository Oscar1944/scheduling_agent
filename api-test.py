import requests
from datetime import datetime, date

# Get holidays
# res = requests.get("https://holidays.abstractapi.com/v1/?api_key=4488dd681b814d0eb554690c40b7622e&country=TW&year=2026&month=3&day=21")
# print(res.text)

# Get datetime
print(datetime.now())
print(date(2026,1,20).weekday())

# Get Gemini-LLM
from google import genai
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyAoBru-W4QfK_f9XJvpKwwRYFnsEIktsl8")

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)