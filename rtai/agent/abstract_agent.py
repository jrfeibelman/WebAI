
from abc import abstractmethod, ABC
from contextlib import contextmanager
from numpy import uint16
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rtai.agent.agent_manager import AgentManager

from rtai.agent.behavior.chat import Chat
from rtai.core.clock import clock
from rtai.utils.datetime import timedelta

class AbstractAgent(ABC):
    """_summary_ Abstract base class to represent an agent."""

    id: uint16 = uint16(0)

    def __init__(self, agent_manager: 'AgentManager'):
        self.agent_mgr = agent_manager
        self._under_interrogation: bool = False
        AbstractAgent.id += 1
        self.id = AbstractAgent.id

    # TODO add funcs for prompt generation and calling LLM
        
    @contextmanager
    def enter_interrogation(self) -> Chat:
        self._under_interrogation = True

        chat = Chat(description=f"Interrogation of {self.get_name()}", creator_id=self.get_id(), address="", start_time=clock.snapshot(), duration=timedelta(seconds=0))
        chat.register_participant(self.get_name())
        self.agent_mgr.chat_mgr.create_chat(chat)

        try:
            yield chat
        finally:
            self._under_interrogation = False
            self.agent_mgr.chat_mgr.delete_chat(chat)

    # @abstractmethod
    # def interrogate(self, question: str) -> str:
    #     pass

    @abstractmethod
    def get_name(self) -> str:
        """_summary_ Get the name of the agent.

        Returns:
            str: Name of the agent.
        """
        pass

    @abstractmethod
    def save_to_file(self, file_path: str):
        """_summary_ Save the state of an agent to a file.

        Args:
            file_path (str): Path to save the agent to.
        """
        pass
    
    @abstractmethod
    def load_from_file(self) -> bool:
        """_summary_ Load the state of an agent from a file.

        Args:
            file_path (str): Path to load the agent from.
        Returns:
            bool: Whether the agent was successfully loaded.
        """
        pass

    def get_id(self) -> uint16:
        """ _summary_ Get the agent's id 
        
        Returns:
            uint16: Agent's id
        """
        return self.id