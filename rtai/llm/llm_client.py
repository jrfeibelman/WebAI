'''
This module contains the LLMClient class, which is responsible for communicating with the LLM server.
'''
from typing import List, Tuple
from guidance import models, gen
import guidance
# from guidance.models.llama_cpp.llama_cpp import LlamaCpp

from rtai.utils.config import Config


class LLMClient:
    model = None

    # TODO make singleton
    # def __new__(cls) -> 'LLMClient':
    #     """ _summary_ Singleton constructor for the LLMClient"""
    #     if not hasattr(cls, '_instance'):
    #         cls._instance = super().__new__(cls)
    #         cls.model = None
    #     return cls._instance
    
    def __init__(self) -> None:
        LLMClient.model = None

    def initialize(self, cfg: Config) -> bool:
        self.cfg: Config = cfg
        LLMClient.model = models.LlamaCpp(cfg.get_value("local_model_path", ""), n_gpu_layers=-1, n_ctx=20000)
        LLMClient.model.echo = False
        return True
            
    @guidance
    def create_daily_tasks(lm, self, persona, num_tasks=3):
        for i in range(num_tasks):
            lm += f'''Briefly describe a task {i+1} that {persona} does in a day in 10 or less words: "{gen(stop=".", name="tasks", temperature=1.0, list_append=True)}"\n'''
        return lm

    @guidance
    def estimate_duration(lm, self, persona, tasks):
        lm += f"Estimate a realistic duration, in hours, of how much time a {persona} would take for each task: \n"
        for i in range(len(tasks)):
            lm += f'''Task {i+1} will take {persona} {gen(stop='"', regex="[0-9]", name="duration", temperature=0.7, max_tokens=10, list_append=True)} hours\n'''
        return lm

    @guidance
    def estimate_start_times(lm, self, persona, tasks):
        lm +=  f"Generate a start time for when {persona} will start each task: \n"
        for i in range(len(tasks)):
            lm += f'''Task {i+1} will start at {gen(stop='"', regex="[0-9]:[0-9][0-9]", name="start_time", temperature=0.7, max_tokens=10, list_append=True)} hours\n'''
        return lm

    @guidance
    def create_interrogation(lm, self, persona, context, question, history):
        # print(f"Type of lm is {type(lm)}, {type(persona)}, {type(context)}, {type(question)}")
        lm += f'''You are {persona}. Answer the question like you are {persona} in 2 lines max, given the history: {history} and context: {context}. Q: {question} A: \n{gen(stop='Q:', name="interrogation", max_tokens=1000)}'''
        return lm

    @guidance
    def create_dialogue(self, persona1, persona2, location):
        lm = LLMClient.model
        lm += f"""
        Generate a short dialogue between {persona1.name} and {persona2.name} in {location}

        {persona1.name} context: {persona1.common_str} {persona1.relationships[persona2.name]}
        {persona2.name} context: {persona2.common_str} {persona2.relationships[persona1.name]}

        Example of dialogue:
        Hank: Howdy, Claire, how's it going?
        Claire: Good, what about you?

        Here is the short dialogue:
        {gen('dialogue', max_tokens=1000)}"""
        # lm = LLMClient.model + dialogue_prompt
        return lm

    def generate_daily_plan(self, persona):
        return ""
    
    # @guidance
    def generate_observation(self, persona, current_action):
        return "Test Observation"
        # lm = LLMClient.model
        # lm += f"Generate an observation that {persona} has about their current action {current_action}:\n{gen('observe', max_tokens=1000)}"
        # return lm['observe']
    
    def generate_daily_schedule(self, persona) -> List[Tuple[str, str, str]]:
        # generate the tasks
        mistral = LLMClient.model
        out1 = mistral + self.create_daily_tasks(persona)
        tasks = out1['tasks']
        # print(tasks)
        # estimate the duration
        out2 = mistral + self.estimate_duration(persona, tasks)
        duration = out2["duration"]
        # print(duration)
        # estimate the start times
        out3 = mistral + self.estimate_start_times(persona, tasks)
        start_time = out3["start_time"]
        # print(start_time)
        # return a list of triples
        return list(zip(tasks, duration, start_time))
    
    def generate_interrogation(self, persona, context, question, history):
        # print("persona", persona)
        # print("retrieved context", context)
        # print("question", question)
        mistral2 = models.LlamaCpp(self.cfg.get_value("local_model_path", ""), n_gpu_layers=-1, n_ctx=2048)
        mistral2.echo = False
        out = mistral2 + self.create_interrogation(persona=persona, context=context, question=question, history=history)
        resp = out["interrogation"]
        return resp

# @guidance
# def generate_dialogue(lm, ):


@guidance
def estimate_importance(lm, concept):
    lm += f"On the scale of 0 to 9, where 0 is purely mundane (e.g., brushing teeth, making bed) and 9 is extremely poignant (e.g., a break up, college acceptance), rate the likely importance of the following piece of memory. Respond with a single integer."
    lm += f'''The piece of memory is {concept} and the importance of the event is {gen(stop='"', regex="[0-9]", name="importance", temperature=0.7, max_tokens=10)}'''
    return lm

def generate_importance(concept):
    mistral3 = models.LlamaCpp("/Users/nyeung/Projects/llama.cpp/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf", n_gpu_layers=-1, n_ctx=2048) # TODO: change this to be configurable
    mistral3.echo = False
    out = mistral3 + estimate_importance(concept)
    resp = out["importance"]
    try:
        importance = int(resp)
    except:
        print("Error: failed to parse importance as integer so labeling concept as importance 5.")
        importance = 5
    print(f"Importance of {concept} is {importance}")
    return importance