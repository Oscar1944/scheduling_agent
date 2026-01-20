from google import genai

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
        # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        # client = genai.Client(api_key="AIzaSyAoBru-W4QfK_f9XJvpKwwRYFnsEIktsl8")
        try:
            response = self.client.models.generate_content(
                model=self.MODEL, contents=message
            )
            return response.text
        except:
            raise ValueError("Error in LLM response generation")

