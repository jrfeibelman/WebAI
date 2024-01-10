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

    def __new__(cls) -> 'LLMClient':
        """ _summary_ Singleton constructor for the LLMClient"""
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
            cls.model = None
        return cls._instance

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
    def generate_interrogation(lm, self, question, context, persona):
        lm += f"""You are {persona}. Answer the question given the context:

        This is the context: {context}
        
        Q: {question}
        A: \n{gen('interrogation', max_tokens=1000)}"""
        return lm

    @guidance
    def create_dialogue(self, persona1, persona2, location):
        dialogue_prompt = f"""
        Generate a short dialogue between {persona1.name} and {persona2.name} in {location}

        {persona1.name} context: {persona1.common_str} {persona1.relationships[persona2.name]}
        {persona2.name} context: {persona2.common_str} {persona2.relationships[persona1.name]}

        Example of dialogue:
        Hank: Howdy, Claire, how's it going?
        Claire: Good, what about you?

        Here is the short dialogue:
        {gen('dialogue', max_tokens=1000)}"""
        lm = LLMClient.model + dialogue_prompt
        return lm["dialogue"]

    def generate_daily_plan(self, persona):
        return ""
    
    @guidance
    def generate_observation(self, persona, current_action):
        lm = LLMClient.model
        lm += f"Generate an observation that {persona} has about their current action {current_action}:\n{gen('observe', max_tokens=1000)}"
        return lm['observe']
    
    def generate_daily_schedule(self, persona) -> List[Tuple[str, str, str]]:
        # generate the tasks
        out1 = LLMClient.model + self.create_daily_tasks(persona)
        tasks = out1['tasks']
        print(tasks)
        # estimate the duration
        out2 = LLMClient.model + self.estimate_duration(persona, tasks)
        duration = out2["duration"]
        print(duration)
        # estimate the start times
        out3 = LLMClient.model + self.estimate_start_times(persona, tasks)
        start_time = out3["start_time"]
        print(start_time)
        # return a list of triples
        return list(zip(tasks, duration, start_time))