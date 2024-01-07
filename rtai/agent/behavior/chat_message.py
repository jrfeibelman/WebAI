from dataclasses import dataclass
from numpy import uint16

from rtai.utils.datetime import datetime

@dataclass
class ChatMessage:
    
    def __init__(self, sender_id: uint16, sender_name: str, message: str, creation_time: datetime=datetime.now()):
        self.sender_id: uint16 = sender_id
        self.sender_name: str = sender_name
        self.message: str = message
        self.creation_time: datetime = creation_time

    def get_sender_id(self) -> uint16:
        return self.sender_id
    
    def __str__(self) -> str:
        return f"[{self.creation_time}] [{self.sender_name}] {self.message}"
    
    def __repr__(self) -> str:
        return str(self)