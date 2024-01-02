
from abc import abstractmethod, ABCMeta

class AbstractAgent(metaclass=ABCMeta):

    def __init__(self):
        pass

    # TODO add funcs for prompt generation and calling LLM

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def save_to_file(self) -> str:
        pass
    
    @abstractmethod
    def load_from_file(self) -> bool:
        pass