'''
This module contains the LLMClient class, which is responsible for communicating with the LLM server.
'''
from openai import OpenAI
from typing import List

from rtai.utils.config import Config

class LLMClient:
    def __init__(self, cfg: Config):
        self.cfg: Config = cfg
        # logging.getLogger("openai").setLevel(logging.ERROR)
        if cfg.get_value("use_server", "False") == "True":
            self.mistral = cfg.get_value("local_", "")
        else:
            self.client = OpenAI(base_url=cfg.get_value("base_url", "http://localhost:1234/v1"),
                    api_key=cfg.get_value("api_key", "not-needed"))
        
    def generate_first_daily_plan(self, wake_up_hour: str) -> str:
        system_prompt = """

        """

        user_prompt = """

        """
        return self.generate_from_prompt(system_prompt, user_prompt)
    
    def generate_daily_plan(self) -> str:
        system_prompt = """

        """

        user_prompt = """

        """
        return self.generate_from_prompt(system_prompt, user_prompt)
    
    def generate_daily_req(self) -> List[str]:
        system_prompt = """

        """

        user_prompt = """

        """
        return self.generate_from_prompt(system_prompt, user_prompt)
    
    def generate_daily_schedule(self, wake_up_hour: str) -> List[str]:
        hour_str = ["00:00 AM", "01:00 AM", "02:00 AM", "03:00 AM", "04:00 AM", 
            "05:00 AM", "06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", 
            "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", 
            "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM", "07:00 PM",
            "08:00 PM", "09:00 PM", "10:00 PM", "11:00 PM"]
        
        system_prompt = """

        """

        user_prompt = """

        """
        return self.generate_from_prompt(system_prompt, user_prompt)
    
    def generate_narration(self) -> str:
        # TODO LATER
        system_prompt = """

        """

        user_prompt = """

        """
        return self.generate_from_prompt(system_prompt, user_prompt)
    
    def generate_from_prompt(self, system_prompt: str = "", user_prompt: str = "") -> str:
        completion = self.client.chat.completions.create(
            model="local-model", # TODO: use config to generlalize this to online hosted models, don't need this field for local model
            messages=[
                {"role": "system", "content": system_prompt}, # can think of the system prompt as context (i.e. memories)
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        return str(completion.choices[0].content).strip()  # todo: more cleaning of the string response
