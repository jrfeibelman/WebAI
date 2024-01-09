
from abc import abstractmethod, ABCMeta
from contextlib import contextmanager
class AbstractAgent(metaclass=ABCMeta):
    """_summary_ Abstract base class to represent an agent."""

    def __init__(self):
        self._under_interrogation: bool = False

    # TODO add funcs for prompt generation and calling LLM
        
    @contextmanager
    def enter_interrogation(self):
        self._under_interrogation = True
        try:
            yield
        finally:
            self._under_interrogation = False

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