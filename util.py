from google import genai

def getToday():
    """
    Get datetime of today
    Return (str): Datetime of today
    """
    # Simulation datetime
    return "2026/1/19"


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


class Guardrail:
    """
    Verify if the LLM resopnse contains content that violate AI governance
    Suggest applying light LLM model to reduce lantency & cost
    """
    def __init__(self, POLICY:str, CORRECT:str, MODEL:LLM):
        self.policy = POLICY
        self.correction = CORRECT
        self.llm = MODEL

    def safety_check(self, conversation, message):
        """
        This is designed for verifying if the given content violate safety policy.
        Input: 
            message (str): the given message
        Return (bool): True, if safety pass. False, if safety fail. [Violation Reason will be attached] 
        """
        instruction = self.policy.format(
            chat_history=conversation,
            message=message
        )
        
        res = self.llm.chat(instruction)
        if res:
            if "[pass]" in res.lower():
                return True, "Safety Pass"
            elif "[fail]" in res.lower():
                return False, res
            else:
                raise ValueError("LLM return unknown result")
        else:
            raise ValueError("LLM return None")
    
    def correct(self, conversation, message, feedback=""):
        """
        Re-write message based on feedback
        Input:
            conversation (str): past chat history
            message (str): the latest message
            feedback (str): feedback from previous round of llm-judge
        Return (str): re-writted message
        """
        instruction = self.correction.format(
            chat_history=conversation,
            message=message,
            feedback=feedback
        )
        res = self.llm.chat(instruction)

        return res
