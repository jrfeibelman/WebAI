import asyncio
from pykka import ThreadingActor

class SecondAgentActor(ThreadingActor):
    def __init__(self, agent_id):
        super().__init__()
        self.agent_id = agent_id

    def on_receive(self, message):
        if message == "Trigger action 1":
            self.perform_action_1()
        elif message == "Trigger action 2":
            self.perform_action_2()
        else:
            print(f"SecondAgentActor {self.agent_id} received an unknown message: {message}")

    def perform_action_1(self):
        print(f"SecondAgentActor {self.agent_id} is performing Action 1")

    def perform_action_2(self):
        print(f"SecondAgentActor {self.agent_id} is performing Action 2")

class AgentActor(ThreadingActor):
    def __init__(self):
        super().__init__()
        self.managed_agents = []
        self.agent_counter = 0

    def on_receive(self, message):
        print(f"AgentActor received message: {message}")
        if message == "Create a new agent":
            new_agent = self.create_new_agent()
            new_agent.tell(f"Hello from agent {new_agent.agent_id}")
        
    def create_new_agent(self):
        agent_id = self.agent_counter
        self.agent_counter += 1
        new_agent = SecondAgentActor.start(agent_id)
        self.managed_agents.append(new_agent)
        return new_agent

def some_condition(message):
    # Define your condition here based on the received message
    return "create_agent" in message.lower() if message == "Create a new agent" else False

async def main():
    # Create AgentActor
    agent = AgentActor.start()

    # Send a message to AgentActor to trigger the creation of a new agent
    agent.tell("Create a new agent")

    # Gather the asynchronous tasks
    tasks = [asyncio.ensure_future(asyncio.sleep(3)), asyncio.ensure_future(agent.stop())]
    await asyncio.gather(*tasks)

# Run the event loop until the coroutine is complete
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
