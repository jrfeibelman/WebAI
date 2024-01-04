from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rtai.agent.agent import Agent

class Cognition:
    def __init__(self, agent: 'Agent'):
        self.agent = agent

    def perceive(self):
        self.observe()
        self.think()
        pass

    def retrieve(self):
        pass

    def think(self):
        pass

    def observe(self):
        pass

    def reflect(self):
        self.retrieve()
        pass

    def act(self):
        pass

    def plan(self, replan=False):
        pass

    def chat(self):
        pass