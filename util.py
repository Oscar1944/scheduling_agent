from google import genai

def getToday():
    """
    Get datetime of today
    Return (str): Datetime of today
    """
    # Simulation datetime
    return "2026/1/19"


def guardrails():
    """
    Verify if the LLM resopnse contains content that violate AI governance
    Return: str
    """

class LLM:
    def __init__(self, API_KEY, MODEL):
        self.API_KEY = API_KEY
        self.MODEL = MODEL
        self.client = genai.Client(api_key=self.API_KEY)

    def chat(self, message):
        """
        Send a message to LLM
        Return (str): LLM response
        """
        # The client gets the API key from the environment variable `GEMINI_API_KEY` as default.
        try:
            response = self.client.models.generate_content(
                model=self.MODEL, contents=message
            )
            return response.text
        except:
            print(response.text)
            raise ValueError("Error in LLM response generation")

