
from rtai.utils.config import Config

from rtai.llm.llm_local import load_model as load_model_llm, create_dialogue as create_dialogue_llm, generate_daily_plan as generate_daily_plan_llm
from tests.mock.llm.llm_local_mock import load_model as load_model_mock, create_dialogue as create_dialogue_mock, generate_daily_plan as generate_daily_plan_mock

model = None
generate_daily_plan = None
create_dialogue = None

def load_model(cfg: Config, test_mode: bool=False):
    global generate_daily_plan
    global create_dialogue

    if not test_mode:
        print("JASON LLM")
        load_model_llm(cfg)
        create_dialogue = create_dialogue_llm
        generate_daily_plan = generate_daily_plan_llm
    else:
        print("JASON MOCK")
        load_model_mock(cfg)
        create_dialogue = create_dialogue_mock
        generate_daily_plan = generate_daily_plan_mock
