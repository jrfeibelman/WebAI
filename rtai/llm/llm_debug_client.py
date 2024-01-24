from llm_client import LLMClient
from typing import List, Tuple

class LLMDebugClient(LLMClient):
    model = None

    def __init__(self):
        super().__init__()

    def initialize(self, cfg) -> bool:
        return super().initialize(cfg)
    
    # insert a plan
    def generate_daily_schedule(self, persona) -> List[Tuple[str, str, str]]:
        if persona.name == "Hank Thompson":
            return [
                ("Wake up and make coffee", "0.25", "9:00"),
                ("Have a chat with Claire Reynolds", "2.25", "9:15"),
                ("Do work on farm", "8", "11:30"),
                ("Eat dinner", "1", "19:30"),
                ("Play video games", "4", "20:30"),
                ("Sleep", "9", "00:30")
            ]        
        else:
            return [
                ("Wake up and shower", "0.25", "9:00"),
                ("Have a chat with Hank Thompson", "2.25", "9:15"),
                ("Conduct fieldwork on ecosystem", "8", "11:30"),
                ("Have dinner", "1", "19:30"),
                ("Watch TV", "4", "20:30"),
                ("Sleep", "9", "00:30")
            ]
