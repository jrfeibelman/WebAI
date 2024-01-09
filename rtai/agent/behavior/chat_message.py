from dataclasses import dataclass
from numpy import uint16

from rtai.utils.datetime import datetime
from rtai.world.clock import clock

@dataclass
class ChatMessage:
    """_summary_ Class to represent a chat message."""
    
    def __init__(self, sender_id: uint16, sender_name: str, message: str):
        """_summary_ Constructor for a chat message.
        
        Args:
            sender_id (uint16): ID of the sender agent.
            sender_name (str): Name of the sender agent.
            message (str): Message sent by the agent
            creation_time (datetime, optional): Creation time of the message. Defaults to datetime.now().
        """
        self.creation_time: datetime = clock.snapshot()
        self.sender_id: uint16 = sender_id
        self.sender_name: str = sender_name
        self.message: str = message

    def get_sender_id(self) -> uint16:
        """_summary_ Get the ID of the sender agent.

        Returns:
            uint16: ID of the sender agent.
        """
        return self.sender_id
    
    def __str__(self) -> str:
        return f"[{self.creation_time}] [{self.sender_name}] {self.message}"
    
    def __repr__(self) -> str:
        return str(self)