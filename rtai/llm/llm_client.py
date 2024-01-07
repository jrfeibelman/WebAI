'''
This module contains the LLMClient class, which is responsible for communicating with the LLM server.
'''
from rtai.utils.config import Config
from openai import OpenAI
import logging
from guidance import models, instruction, gen

class LLMClient:
    def __init__(self, cfg: Config):
        self.cfg: Config = cfg
        # logging.getLogger("openai").setLevel(logging.ERROR)
        if cfg.get_value("use_server", False):
            self.mistral = cfg.get_value("local_", "")
        else:
            self.client = OpenAI(base_url=cfg.get_value("base_url", "http://localhost:1234/v1"),
                    api_key=cfg.get_value("api_key", "not-needed"))

    def generate_from_prompt(self, system_prompt: str = "", user_prompt: str = ""):
        completion = self.client.chat.completions.create(
            model="local-model", # TODO: use config to generlalize this to online hosted models, don't need this field for local model
            messages=[
                {"role": "system", "content": system_prompt}, # can think of the system prompt as context (i.e. memories)
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        return str(completion.choices[0].content).strip()  # todo: more cleaning of the string response
