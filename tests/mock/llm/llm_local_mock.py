'''
Scaffolding to use local LLM model without server
'''
from rtai.utils.config import Config

# global llm model

model = None

def load_model(cfg: Config):
    pass

def create_dialogue(persona1, persona2, location):
    pass

def generate_daily_plan(persona):
    pass

def generate_daily_schedule(persona):
    return [
        ("Wake up and make coffee", "0.5", "9:00"),
        ("Have chat", "2", "9:30"),
        ("Attend Work", "8", "11:30"),
        ("Have dinner", "1", "19:30"),
        ("Play video games", "4", "20:30"),
        ("Sleep", "9", "00:30")
    ]
