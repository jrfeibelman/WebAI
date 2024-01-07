from typing import TYPE_CHECKING

from rtai.utils.logging import debug
from rtai.core.event import Event
from rtai.agent.behavior.chat import Chat

if TYPE_CHECKING:    
    from rtai.agent.agent import Agent

class Conversing:
    """_summary_ Class to represent an agent's conversing behavior."""
    def __init__(self, agent: 'Agent'):
        """_summary_ Constructor for an agent's conversing behavior.

        Args:
            agent (Agent): Agent to which the behavior belongs.
        """
        self.agent: 'Agent' = agent

    def reject_chat_request(self, event: Event) -> None:
        """_summary_ Reject a chat request.

        Args:
            event (Event): Event containing the chat request.
        """
        debug("Agent [%s] rejected chat request from [%s]" % (self.agent.get_name(), event.get_sender()))

    def receive_chat_request(self, event: Event) -> None:
        """_summary_ Receive a new chat request.

        Args:
            event (Event): Event containing the chat request.
        """
        debug("Agent [%s] received chat request [%s] from [%s]" % (self.agent.get_name(), event.get_message().seq_num, event.get_sender()))
    
        if len(self.agent.s_mem.chatting_with) > 0:
            if self.agent.s_mem.chatting_with == event.get_sender():
                # If already chatting with requester, then chose which chat to use based on lowest seq num
                if self.agent.s_mem.current_chat.get_id() > event.get_message().get_id():
                    # Accept received chat, discard owned chat
                    self.agent.agent_mgr.chat_mgr.delete_chat(self.agent.s_mem.current_chat)
                    self.initiate_chat(event.get_message(), event.get_sender())
                else:
                    # Accept owned chat, discard received chat
                    debug("Agent [%s] discarded chat request [%s] from [%s]. Using owned chat" % (self.agent.get_name(), event.get_message().seq_num, event.get_sender()))

            # Already chatting
            elif self.agent.s_mem.current_chat.get_id() != event.get_message().get_id():
                # If in a chat and its not the chat requested
                self.reject_chat_request(event)
            else:
                # Already registered chat
                pass
        else:
            self.initiate_chat(event.get_message(), event.get_sender())

    def end_chat(self, chat: Chat) -> None:
        """_summary_ End a chat.

        Args:
            chat (Chat): Chat to end.
        """
        debug("Agent [%s] ended chat [%s] with [%s]" % (self.agent.get_name(), chat.seq_num, self.agent.s_mem.chatting_with))

    def respond_to_chat(self, chat: Chat) -> None:
        """_summary_ Respond to a chat.

        Args:
            chat (Chat): Chat to respond to.
        """
        debug("Agent [%s] responded to chat [%s] with [%s]" % (self.agent.get_name(), chat.seq_num, self.agent.s_mem.chatting_with))

    def initiate_chat(self, chat: Chat, other_agent_name: str) -> None:
        """_summary_ Initiate a chat.

        Args:
            chat (Chat): Chat to initiate.
            other_agent_name (str): Name of the other agent in the chat.
        """
        debug("Agent [%s] initiated chat [%s] with [%s]" % (self.agent.get_name(), chat.seq_num, other_agent_name))
        self.agent.s_mem.chatting_with = other_agent_name
        self.agent.s_mem.current_chat = chat
        chat.register_participant(self.agent.get_name())