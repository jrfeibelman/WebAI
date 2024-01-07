from numpy import uint64, uint16
from typing import Set

from rtai.utils.datetime import datetime, timedelta
from rtai.agent.behavior.action import Action

class Chat(Action):
    seq_num: uint64 = uint64(0)

    def __init__(self, description: str, creator_id: uint16, address: str, start_time: datetime, duration: timedelta, end_time: datetime=None):
        super().__init__(description=description, address=address, start_time=start_time, duration=duration, end_time=end_time)
        self.participants: Set[str] = set()
        self.creator_id: uint16 = creator_id
        self.alive: bool = False

        self.seq_num = Chat.seq_num
        Chat.seq_num += 1

    def __str__(self):
        return f"Chat [{self.seq_num}] [{self.description}]"

    def __repr__(self):
        return str(self)
    
    def mark_completed(self):
        super().mark_completed()
        self.alive = False
    
    def set_alive(self, alive: bool):
        self.alive = alive
    
    def get_id(self) -> uint64:
        return self.seq_num
    
    def get_creator_id(self) -> uint16:
        return self.creator_id

    def _calc_end_time(self, start_time: datetime, duration: timedelta) -> datetime:
        if start_time._data.second != 0:
            start_time.replace_time(seconds=0)
        return (start_time + duration)
    
    def register_participant(self, agent_name: str):
        self.participants.add(agent_name)
        