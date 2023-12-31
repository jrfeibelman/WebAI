'''
Scaffolding to use local LLM model without server
'''
from guidance import models, instruction, gen
import guidance

@guidance
def daily_plan(lm, persona):
    lm += f'''Generate 3 specific tasks that a {persona} does in a day: \n'''
    for i in range(3):
        lm += f'''Task {i+1}: "{gen(stop='"', name="tasks", temperature=1.0, list_append=True, max_tokens=100)}"\n'''
    return lm

@guidance
def duration(lm, persona, tasks):
    lm += "Estimate a realistic duration, in hours, of how much time a {persona} would take for each task: \n"
    for i in range(len(tasks)):
        lm += f'''Task {i+1} will take {persona} {gen(stop='"', regex="[0-9]", name="duration", temperature=0.7, max_tokens=10, list_append=True)} hours\n'''
    return lm

class LocalLLM():
    def __init__(self, model_path):
        self.llm = models.LlamaCpp(model_path, n_gpu_layers=-1)  # for mps, TODO: change so can work off mac

    def generate_daily_plan(self, persona):
        return self.llm + daily_plan(persona)
    
    def generate_duration(self, persona, tasks):
        return self.llm + duration(persona, tasks)