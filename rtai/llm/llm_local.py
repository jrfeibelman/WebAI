'''
Scaffolding to use local LLM model without server
'''
from guidance import models, gen
import guidance
from rtai.utils.config import Config
from tests.mock.llm.llm_local_mock import generate_daily_plan as generate_daily_plan_mock

model = None # global model variable

def load_model(cfg: Config):
    global model
    model = models.LlamaCpp(cfg.get_value("local_model_path", ""), n_gpu_layers=-1, n_ctx=2048)
    # model.echo = False

@guidance
def create_daily_tasks(lm, persona, num_tasks=3):
    for i in range(num_tasks):
        lm += f'''Briefly describe a task {i+1} that {persona} does in a day in 10 or less words: "{gen(stop=".", name="tasks", temperature=1.0, list_append=True)}"\n'''
    return lm

@guidance 
def create_thought(lm, persona, situation, num_thoughts=3):
    for i in range(num_thoughts):
        lm += f'''Generate a short thought {i+1} that {persona} might have in the following situation {situation}: "{gen(stop='.', name="thoughts", temperature=1.0, list_append=True)}"\n'''
    return lm

@guidance
def estimate_duration(lm, persona, tasks):
    lm += f"Estimate a realistic duration, in hours, of how much time a {persona} would take for each task: \n"
    for i in range(len(tasks)):
        lm += f'''Task {i+1} will take {persona} {gen(stop='"', regex="[0-9]", name="duration", temperature=0.7, max_tokens=10, list_append=True)} hours\n'''
    return lm

@guidance
def estimate_start_times(lm, persona, tasks):
    lm += f"Generate a start time for when {persona} will start each task: \n"
    for i in range(len(tasks)):
        lm += f'''Task {i+1} will start at {gen(stop='"', regex="[0-9]:[0-9][0-9]", name="start_time", temperature=0.7, max_tokens=10, list_append=True)} hours\n'''
    return lm

@guidance
def estimate_importance(lm, persona, observations):
    lm += f"On the scale of 1 to 10, where 1 is purely mundane and 10 is extremely important (e.g., a break up, college acceptance), rate the importance of the following observation to {persona}: \n" 
    for i in range(len(observations)):
        lm += f'''Observation: {observations[i]}. The importance of this observation is: {gen(stop='"', regex="[0-9]", name="importance", temperature=0.7, max_tokens=10, list_append=True)} \n'''
    return lm



@guidance
def create_dialogue(persona1, persona2, location):
    # TODO: debug this diaglogue for robustness
    global model
    dialogue_prompt = f"""
    Generate a short dialogue between {persona1.name} and {persona2.name} in {location}

    {persona1.name} context: {persona1.common_str} {persona1.relationships[persona2.name]}
    {persona2.name} context: {persona2.common_str} {persona2.relationships[persona1.name]}

    Example of dialogue:
    Hank: Howdy, Claire, how's it going?
    Claire: Good, what about you?

    Here is the short dialogue:
    {gen('dialogue', max_tokens=1000)}"""
    lm = model + dialogue_prompt
    return lm["dialogue"]

def generate_daily_plan(persona):
    print("CALLED")
    global model
    # generate the tasks
    out1 = model + create_daily_tasks(persona)
    tasks = out1['tasks']
    # print(tasks)
    # estimate the duration
    out2 = model + estimate_duration(persona, tasks)
    duration = out2["duration"]
    # print(duration)
    # estimate the start times
    out3 = model + estimate_start_times(persona, tasks)
    start_time = out3["start_time"]
    # print(start_time)
    # return a list of triples
    return list(zip(tasks, duration, start_time))

def generate_thought(persona, situation):
    global model
    out = model + create_thought(persona, situation)
    thoughts = out["thoughts"]
    print(thoughts)

    out2 = model + estimate_importance(persona, thoughts)
    importance = out2["importance"]
    return list(zip(thoughts, importance))