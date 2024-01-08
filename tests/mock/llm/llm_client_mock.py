from pytest import fixture
from typing import List, Tuple

from guidance import models, gen
import guidance

from rtai.llm.llm_client import LLMClient
from rtai.utils.config import Config
from rtai.agent.persona import Persona
from rtai.utils.config import Config

@fixture(scope="session")
def mock_llm_client(mock_config_base: Config):
    return LLMTestClient(mock_config_base)

class LLMTestClient:
    model = None

    def __new__(cls) -> 'LLMTestClient':
        """ _summary_ Singleton constructor for the LLMClient"""
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, cfg: Config) -> bool:
        self.cfg: Config = cfg
        return True
                
    def create_daily_tasks(self, lm, persona, num_tasks=3):
        return ""

    def estimate_duration(self, lm, persona, tasks):
        return ""

    def estimate_start_times(self, lm, persona, tasks):
        return ""
    
    def create_dialogue(self, persona1, persona2, location):
        return ""

    def generate_daily_plan(self, persona):
        return ""

    def generate_daily_schedule(self, persona, wake_up_hour) -> List[Tuple[str, str, str]]:
        print("CALLED")
        return [
            ("Wake up and make coffee", "0.5", "9:00"),
            ("Have chat", "2", "9:30"),
            ("Attend Work", "8", "11:30"),
            ("Have dinner", "1", "19:30"),
            ("Play video games", "4", "20:30"),
            ("Sleep", "9", "00:30")
        ]

        






    # def __init__(self, cfg: Config):
    #     super().__init__(cfg)
    
    # def generate_first_daily_plan(self, wake_up_hour: str) -> str:
    #     return self.generate_daily_plan()
    
    # def generate_daily_plan(self) -> List[str]:
    #     return [
    #             "Wake up", 
    #             "Get washed up",
    #             "Cook and eat breakfast",
    #             "Attend work",
    #             "Get lunch at work",
    #             "Pick up daughter from school",
    #             "Get more groceries",
    #             "Go home and cook dinner",
    #             "Have dinner with Dolores",
    #             "Patrol the streets of New York City for crime",
    #             "Go home and to bed",
    #         ]
    
    # def generate_daily_req(self) -> str:
    #     return 'Get more groceries, attend work at Goliath National Bank, have dinner with Dolores, pick up daughter from school, patrol the streets of New York City for crime'
    
    # def generate_daily_schedule(self, persona: Persona, wake_up_hour: str) -> List[Tuple[str]]:
    #     """(start_time, duration, text)
    #     """
    #     test_agents = ['Hank Thompson', 'Claire Reynolds']
    #     chat_recipient = test_agents[1] if persona.name == test_agents[0] else test_agents[0]
    #     return [
    #         # ("6:30 AM", "0.25", "Wake up and get washed up"),
    #         ("6:30 AM", "3.25", "Chat with %s" % chat_recipient),
    #         # ("7:00 AM", "0.5", "Cook and eat breakfast"),
    #         ("9:45 AM", "6.25", "Attend work"),
    #         ("04:00 PM", "0.5", "Pick up daughter from school"),
    #         ("04:30 PM", "0.5", "Get more groceries"),
    #         ("05:00 PM", "1.0", "Go home and cook dinner"),
    #         ("06:00 PM", "1.0", "Have dinner with Dolores"),
    #         ("07:00 PM", "4.5", "Watch TV"),
    #         ("11:30 PM", "0.5", "Walk aronud"),
    #         ("12:00 AM", "0.0", "Go home and to bed"),
    #     ]

    # def generate_from_prompt(self, system_prompt: str = "", user_prompt: str = "") -> str:
    #     return ""

