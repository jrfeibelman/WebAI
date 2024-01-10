from numpy import uint64, uint16
from typing import Set, List

from rtai.utils.datetime import datetime, timedelta
from rtai.agent.behavior.action import Action

class Chat(Action):
    """_summary_ Class to represent a chat behavior."""

    seq_num: uint64 = uint64(0)

    def __init__(self, description: str, creator_id: uint16, address: str, start_time: datetime, duration: timedelta, end_time: datetime=None):
        """_summary_ Constructor for a chat object, representing a conversation between agents.

        Args:
            description (str): Description of the chat.
            creator_id (uint16): ID of the agent that created the chat.
            address (str): Address of the chat.
            start_time (datetime): Start time of the chat.
            duration (timedelta): Planned duration of the chat.
            end_time (datetime, optional): End time of the chat. Defaults to None. If None, it is calculated from start_time and duration.
        """

        super().__init__(description=description, address=address, start_time=start_time, duration=duration, end_time=end_time)
        self.participants: Set[str] = set()
        self.creator_id: uint16 = creator_id
        self.alive: bool = False
        self.finished_conversation: List[str] = []

        self.seq_num = Chat.seq_num
        Chat.seq_num += 1

    def __str__(self) -> str:
        return f"Chat [{self.description}]" if len(self.finished_conversation) == 0 else f"Chat [{self.description}] [{self.finished_conversation}]"

    def __repr__(self) -> str:
        return f"Chat [{self.seq_num}] [{self.description}]"
    
    def mark_completed(self) -> None:
        """_summary_ Mark the chat as completed and calculate the chat duration."""
        super().mark_completed()
        self.alive = False
    
    def set_alive(self, alive: bool) -> None:
        """_summary_ Set the chat as alive or not.

        Args:
            alive (bool): True if the chat is alive, False otherwise.
        """
        self.alive = alive
    
    def get_id(self) -> uint64:
        """_summary_ Get the ID of the chat.

        Returns:
            uint64: ID of the chat.
        """
        return self.seq_num
    
    def get_creator_id(self) -> uint16:
        """_summary_ Get the ID of the creator agent.

        Returns:
            uint16: ID of the creator agent.
        """
        return self.creator_id
    
    def register_participant(self, agent_name: str) -> None:
        """_summary_ Register a participant to the chat."""
        self.participants.add(agent_name)
        