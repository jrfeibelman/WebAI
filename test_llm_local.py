from rtai.llm.llm_local import load_model, generate_daily_plan
from rtai.utils.config import YamlLoader

cfg = YamlLoader.load("configs/rtai_jason.yaml")
load_model(cfg.expand("LLMClient"))
persona = "Bob Joe"

print(generate_daily_plan(persona))
