from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from rtai.agent.agent import Agent

from rtai.core.event import Event, EventType
from rtai.utils.logging import log_transcript, info
from rtai.agent.cognition.concept_node import ConceptNode
from rtai.utils.datetime import datetime, timedelta
from rtai.agent.behavior.action import Action
from rtai.agent.behavior.chat import Chat
from rtai.agent.behavior.chat_message import ChatMessage
from rtai.agent.behavior.abstract_behavior import AbstractBehavior
from rtai.world.clock import clock

class Cognition:
    """
    Class to represent Cognition of agent
    
    Steps:
        - perceive -> retrieve -> observe -> think -> plan -> act -> reflect
    
    """
    counter: int = 0 # TODO delete

    def __init__(self, agent: 'Agent'):
        """_summary_ Constructor for Cognition class.

        Args:
            agent (Agent): agent that this cognition belongs to
        """
        self.agent = agent

    def perceive(self) -> List:
        """_summary_ Perceive the environment and return a list of events.
        
        Returns:
            List: List of events perceived by the agent.

        Create Thoughts (SKIP FOR NOW)
            - Analyze surroundings: perceives events around the persona and saves events to the memory ?
        """
        self.observe()
        return []

    def retrieve(self):
        """ _summary_ Retrieve events and thoughts from long term memory.
        
        Retreive
            From simularca:
                This function takes the events that are perceived by the persona as input
                and returns a set of related events and thoughts that the persona would 
                need to consider as context when planning. 

                INPUT: 
                    perceived: a list of event <ConceptNode>s that represent any of the events
                    `         that are happening around the persona. What is included in here
                            are controlled by the att_bandwidth and retention 
                            hyper-parameters.
                OUTPUT: 
                    retrieved: a dictionary of dictionary. The first layer specifies an event, 
                            while the latter layer specifies the "curr_event", "events", 
                            and "thoughts" that are relevant.
        """
        # TODO neil implement retrieve
        pass

    def observe(self):
        """ _summary_ Observe the environment """
        # First get environment around user
        # world = self.agent.agent_mgr.world

        # Get data needed to create observation

        # Generate observation
        current_action = self.agent.s_mem.current_action if len(self.agent.s_mem.chatting_with) == 0 else self.agent.s_mem.current_chat
        observation: str = self.agent.llm_client.generate_observation(self.agent.persona, current_action)

        # Save observation to long term memory
        node: ConceptNode = self.agent.l_mem.add_concept(observation, EventType.ThoughtEvent)
        log_transcript(self.agent.get_name(), clock.get_time_str(), 'Thought(Observation)', f"{node.summary()}")
        return node


    def reflect(self):
        self.retrieve()
        pass

    def determine_action(self) -> AbstractBehavior:
        """ _summary_ Determine the next action sequence for agent to take and calls add_new_action.

        Returns:
            AbstractBehavior: The next action to be taken by the agent.
        
        TODO - As a part of this, persona may need to decompose hourly schedule into smaller tasks for long duration events   
        TODO - There might be core events, such as meals and bed time, which are tasks that must be accomplished on a given day
        TODO - There might be fixed events such as work and events shared with other agents, which are tasked that have non-negotiable start times

        Example Hourly Sched:
            ("6:30 AM", "0.5", "Wake up and get washed up"),
            ("7:00 AM", "0.5", "Cook and eat breakfast"),
            ("7:30 AM", "8.5", "Attend work"),
            ("04:00 PM", "0.5", "Pick up daughter from school"),
            ("04:30 PM", "0.5", "Get more groceries"),
            ("05:00 PM", "1.0", "Go home and cook dinner"),
            ("06:00 PM", "1.0", "Have dinner with Dolores"),
            ("07:00 PM", "4.5", "Patrol the streets of New York City for crime"),
            ("11:30 PM", "0.5", "Have conversation with Batman about Joker's latest crime"),
            ("12:00 AM", "0.0", "Go home and go to sleep"),
        """
        action_start: datetime = clock.snapshot()

        # Get current index into daily schedule
        # BUG if first day and start when not sleeping...
        if self.agent.s_mem.daily_schedule_idx == 0 and not self.agent.is_sleeping:
            # Schedule sleep --> Wakeup event
            self.agent.is_sleeping = True
            action_desc = "Sleep"
            # print(self.agent.s_mem.daily_schedule)
            wake_up_hour_str = self.agent.s_mem.daily_schedule[0][2] # TODO wakeup hour by LLM or by other func?
            action_dur = action_start.get_timedelta_from_time_str(wake_up_hour_str)
            self.agent.go_to_sleep()
        elif self.agent.s_mem.daily_schedule_idx >= len(self.agent.s_mem.daily_schedule):
            # TODO end of schedule, do nothing
            return
        else:
            self.agent.s_mem.current_action.mark_completed()

            action_desc, tmp_dur, planned_start_time = self.agent.s_mem.daily_schedule[self.agent.s_mem.daily_schedule_idx] # TODO use action_start

            action_dur = timedelta(minutes=int(float(tmp_dur) * 60))
            self.agent.s_mem.daily_schedule_idx += 1

            if self.agent.s_mem.daily_schedule_idx == 0 and self.agent.is_sleeping:
                self.agent.is_sleeping = False

        action_address = 'Test Address' # TODO add locations of actions from world
        action_start_str = action_start.get_time_str()
        completed_action = self.agent.s_mem.current_action

        if self._is_chat(action_desc):
            # TODO restructure chat functionality
            recipient = self._get_chat_recipient(action_desc)
            new_action: Chat = self.agent.s_mem.add_new_chat(action_address=action_address,
                                    action_start_time=action_start,
                                    action_duration=action_dur,
                                    action_description=action_desc)
            self.agent.agent_mgr.chat_mgr.create_chat(new_action)
            self.agent.conversing.initiate_chat(new_action, recipient)
            e = Event.create_chat_event(self.agent, new_action, recipient)

            if len(self.agent.s_mem.chatting_with) != 0:
                # TODO already chatting
                pass
        
        else:
            new_action: Action = self.agent.s_mem.add_new_action(action_address=action_address,
                                    action_start_time=action_start,
                                    action_duration=action_dur,
                                    action_description=action_desc)
            e = Event.create_action_event(self.agent, new_action)

        # Dispatch event to worker queue
        self.agent.agent_mgr.dispatch_to_queue(e)

        # Only add action to long memory once it completes or add it here?
        if completed_action.address:
            if isinstance(self.agent.s_mem.current_action, Chat):
                self.conversing.end_chat(completed_action)
                convo = self.agent.agent_mgr.chat_mgr.get_chat_history(completed_action)
                completed_action.finished_conversation = convo
                self.agent.l_mem.add_concept(completed_action, EventType.ChatEvent)
            else:
                self.agent.l_mem.add_concept(completed_action, EventType.ActionEvent)

        log_transcript(self.agent.get_name(), action_start_str, 'Action', action_desc)
        
        # Increment index to next action
        self.agent.s_mem.current_action = new_action

        return new_action

    def plan(self, replan: bool=False, new_day: bool=False, first_day: bool=False) -> ConceptNode:
        """ _summary_ Create a plan for the day and save it to long term memory.

        Args:
            replan (bool, optional): True if the plan is being replanned, False otherwise. Defaults to False.
            new_day (bool, optional): True if the plan is being created for a new day, False otherwise. Defaults to False.
            first_day (bool, optional): True if the plan is being created for the first day of the simulation, False otherwise. Defaults to False.
        Returns:
            ConceptNode: The plan for the day.
        """

        wake_up_hour = ""

        if first_day:
            # Generate the very first daily plan
            self.agent.s_mem.generate_first_daily_plan(wake_up_hour)

        elif new_day:
            wake_up_hour = self.agent.s_mem.generate_wake_up_hour()
            
            # Create new daily plan
            self.agent.s_mem.generate_daily_plan()

        # log_transcript(self.agent.get_name(), clock.get_time_str(), 'Thought(Plan)', 'Daily Plan: %s' % self.agent.s_mem.daily_plan)

        # Generate list of daily requirements for the day
        # self.agent.s_mem.generate_daily_req()

        # log_transcript(self.agent.get_name(), clock.get_time_str(), 'Thought(Plan)', 'Daily Requirements: %s' % self.agent.s_mem.daily_req)

        # Create hourly schedule for the persona - list of todo items where each has a duration that adds up to a full day
        self.agent.s_mem.generate_hourly_schedule(self.agent.persona, wake_up_hour)

        log_transcript(self.agent.get_name(), clock.get_time_str(), 'Thought(Plan)', 'Daily Schedule: %s' % self.agent.s_mem.daily_schedule)

        # Save daily requirements to long term memory
        date_str = clock.get_date_str()
        thought = f"This is {self.agent.persona.name}'s plan for {date_str}:"
        for i in self.agent.s_mem.daily_schedule:
            thought += f" {i},"
        thought = thought[:-1] + "."

        node: ConceptNode = self.agent.l_mem.add_concept(thought, EventType.ThoughtEvent)
        log_transcript(self.agent.get_name(), clock.get_time_str(), 'Thought(Plan)', f"{node.summary()} --> {node.content}")
        return node

    def chat(self) -> None:
        """ _summary_ Participate in a chat with another agent"""

        history = self.agent.agent_mgr.chat_mgr.get_chat_history(self.agent.s_mem.current_chat)
        
        if len(history) == 0 and self.agent.s_mem.current_chat.get_creator_id() == self.agent.get_id():
            # Generate first chat of conversation
            new_msg = ChatMessage(sender_id=self.agent.get_id(), sender_name=self.agent.get_name(), message='Chat[%s][%s]' % (self.agent.get_name(), Cognition.counter))
            history.append(new_msg)
            Cognition.counter += 1
            self.agent.s_mem.current_chat.set_alive(True)
            log_transcript(self.agent.get_name(), clock.get_time_str(), 'Chat', new_msg)
        elif len(history) > 0 and history[-1].sender_id != self.agent.get_id():
            # your turn to generate chat
            new_msg = ChatMessage(sender_id=self.agent.get_id(), sender_name=self.agent.get_name(), message='Chat[%s][%s]' % (self.agent.get_name(), Cognition.counter))
            history.append(new_msg)
            Cognition.counter += 1
            log_transcript(self.agent.get_name(), clock.get_time_str(), 'Chat', new_msg)
        else:
            # wait for other person to generate chat
            pass

    def _get_chat_recipient(self, desc: str) -> str:
        """ _summary_ Get the recipient of the chat from the description of the chat.

        Args:
            desc (str): Description of the chat event.
        Returns:
            str: Name of the recipient of the chat.

        TODO make func more robust -> lots of assumptions
        - Have LLM say whether it is chat or not rather than parsing desc
        """
        d = desc.lower()
        var_chat = d.split('chat')
        var_speak = d.split('speak')
        var_talk = d.split('talk')

        if len(var_chat) > 1:
            recipient = " ".join(desc.split('hat with ')[1].split(' ')[0:2])
        elif len(var_speak) > 1:
            recipient = " ".join(desc.split('peak with ')[1].split(' ')[0:2])
        elif len(var_talk) > 1:
            recipient = " ".join(desc.split('alk with ')[1].split(' ')[0:2])

        if len(recipient) == 0:
            return ''
    
        last = recipient[-1]
        if last == ',' or last == '.':
            recipient = recipient[:-1]

        return recipient
    
    def _is_chat(self, desc: str) -> str:
        """ _summary_ Determine if the description is a chat event.

        Args:
            desc (str): Description of the event.
        Returns:
            str: True if the event is a chat event, False otherwise.
        """
        
        d = desc.lower()
        return 'chat' in d or 'speak' in d or 'talk' in d