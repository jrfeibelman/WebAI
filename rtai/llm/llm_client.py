'''
This module contains the LLMClient class, which is responsible for communicating with the LLM server.
'''
from rtai.utils.config import Config
from openai import OpenAI

class LLMClient:
    def __init__(self, cfg: Config):
        self.cfg: Config = cfg
        self.client = OpenAI(base_url=cfg.get_value("base_url", "http://localhost:1234/v1"),
                    api_key=cfg.get_value("api_key", "not-needed"))

    def generate_from_prompt(self, prompt: str):
        completion = self.client.chat.completions.create(
            model="local-model", # TODO: use config to generlalize this to online hosted models, don't need this field for local model
            messages=[
                {"role": "system", "content": "You are a storyteller. Generate short descriptions of the following characters"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return str(completion.choices[0].message).strip()

