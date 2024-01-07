from numpy import uint64
from typing import List, Dict, TypeAlias

from rtai.agent.behavior.chat_message import ChatMessage
from rtai.agent.behavior.chat import Chat

ChatHistory: TypeAlias = List[ChatMessage]
ChatRegistry: TypeAlias = Dict[uint64, ChatHistory]

class ChatManager:
    """ _summary_ Class to manage all the different chats between agents"""
    def __init__(self):
        """ _summary_ Constructor for the Chat Manager. """
        self.chat_registry: ChatRegistry = dict()

    def write_to_chat(self, chat: Chat, message: ChatMessage) -> None:
        """ _summary_ Write a message to a chat
        
        Args:
            chat (Chat): Chat to write to
            message (ChatMessage): Message to write
        """
        self.chat_registry[chat.get_id()].append(message)

    def get_chat_history(self, chat: Chat) -> ChatHistory:
        """ _summary_ Get the history of a chat

        Args:
            chat (Chat): Chat to get history of
        Returns:
            ChatHistory: History of chat
        """
        return self.chat_registry[chat.get_id()]
    
    def create_chat(self, chat: Chat) -> None:
        """ _summary_ Create a new chat

        Args:
            chat (Chat): Chat to create
        """
        self.chat_registry[chat.get_id()] = []

    def delete_chat(self, chat: Chat) -> None:
        """ _summary_ Delete a chat

        Args:
            chat (Chat): Chat to delete
        """
        del self.chat_registry[chat.get_id()]