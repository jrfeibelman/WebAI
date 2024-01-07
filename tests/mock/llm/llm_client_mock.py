from pytest import fixture
from typing import List, Tuple

from rtai.llm.llm_client import LLMClient
from rtai.utils.config import Config
from rtai.agent.persona import Persona

@fixture(scope="session")
def mock_llm_client(mock_config_base: Config):
    return LLMTestClient(mock_config_base)

class LLMTestClient(LLMClient):
    def __init__(self, cfg: Config):
        super().__init__(cfg)
    
    def generate_first_daily_plan(self, wake_up_hour: str) -> str:
        return self.generate_daily_plan()
    
    def generate_daily_plan(self) -> List[str]:
        return [
                "Wake up", 
                "Get washed up",
                "Cook and eat breakfast",
                "Attend work",
                "Get lunch at work",
                "Pick up daughter from school",
                "Get more groceries",
                "Go home and cook dinner",
                "Have dinner with Dolores",
                "Patrol the streets of New York City for crime",
                "Go home and to bed",
            ]
    
    def generate_daily_req(self) -> str:
        return 'Get more groceries, attend work at Goliath National Bank, have dinner with Dolores, pick up daughter from school, patrol the streets of New York City for crime'
    
    def generate_daily_schedule(self, persona: Persona, wake_up_hour: str) -> List[Tuple[str]]:
        """(start_time, duration, text)
        """
        test_agents = ['Hank Thompson', 'Claire Reynolds']
        chat_recipient = test_agents[1] if persona.name == test_agents[0] else test_agents[0]
        return [
            # ("6:30 AM", "0.25", "Wake up and get washed up"),
            ("6:30 AM", "3.25", "Chat with %s" % chat_recipient),
            # ("7:00 AM", "0.5", "Cook and eat breakfast"),
            ("9:45 AM", "6.25", "Attend work"),
            ("04:00 PM", "0.5", "Pick up daughter from school"),
            ("04:30 PM", "0.5", "Get more groceries"),
            ("05:00 PM", "1.0", "Go home and cook dinner"),
            ("06:00 PM", "1.0", "Have dinner with Dolores"),
            ("07:00 PM", "4.5", "Watch TV"),
            ("11:30 PM", "0.5", "Walk aronud"),
            ("12:00 AM", "0.0", "Go home and to bed"),
        ]

    def generate_from_prompt(self, system_prompt: str = "", user_prompt: str = "") -> str:
        return ""

