from pytest import fixture
from typing import List

from rtai.llm.llm_client import LLMClient
from rtai.utils.config import Config

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
    
    def generate_daily_schedule(self, wake_up_hour: str) -> List[str]:
        return [
            "6:30 AM: Wake up and get washed up",
            "7:00 AM: Cook and eat breakfast",
            "7:30 AM: Attend work",
            "9:00 AM: Attend work",
            "10:00 AM: Attend work",
            "11:00 AM: Attend work",
            "12:00 PM: Get lunch at work",
            "01:00 PM: Attend work",
            "02:00 PM: Attend work",
            "03:00 PM: Attend work",
            "04:00 PM: Attend work",
            "05:00 PM: Pick up daughter from school",
            "05:30 PM: Get more groceries",
            "06:00 PM: Go home and cook dinner",
            "07:00 PM: Have dinner with Dolores",
            "08:00 PM: Patrol the streets of New York City for crime",
            "09:00 PM: Patrol the streets of New York City for crime",
            "10:00 PM: Patrol the streets of New York City for crime",
            "11:00 PM: Patrol the streets of New York City for crime",
            "12:00 AM: Go home and to bed",
        ]

    def generate_from_prompt(self, system_prompt: str = "", user_prompt: str = "") -> str:
        return ""

