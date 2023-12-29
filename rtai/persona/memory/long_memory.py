from typing import Tuple
from numpy import uint64, uint32
from datetime import datetime

from rtai.core.event import EventType

class ConceptNode:
        # node_id: str
        # node_count: uint64
        # type_count: uint64
        # event_type: EventType
        # depth: uint64

        # created: datetime
        # expiration: datetime
        # last_accessed: datetime

        # subject = subject
        # predicate = predicate
        # obj = obj

        # description = description
        # embedding_key = embedding_key
        # poignancy = poignancy
        # keywords = keywords
        # filling = filling

    def __init__(self,
            node_id, node_count, type_count, event_type, depth,
            created, expiration, 
            subject, predicate, obj,
            description, embedding_key, poignancy, keywords, filling): 
        
        self.node_id = node_id
        self.node_count = node_count
        self.type_count = type_count
        self.event_type = event_type
        self.depth = depth

        self.created = created
        self.expiration = expiration
        self.last_accessed = self.created

        self.subject = subject
        self.predicate = predicate
        self.obj = obj

        self.description = description
        self.embedding_key = embedding_key
        self.poignancy = poignancy
        self.keywords = keywords
        self.filling = filling

    def summary(self) -> Tuple[str, str, str]:
        return (self.subject, self.predicate, self.object)

class LongTermMemory:
    def __init__(self):
        self.id_to_node = dict()

        self.seq_event = []
        self.seq_thought = []
        self.seq_chat = []

        self.kw_to_event = dict()
        self.kw_to_thought = dict()
        self.kw_to_chat = dict()

        self.kw_strength_event = dict()
        self.kw_strength_thought = dict()

        # self.embeddings = json.load(open(f_saved + "/embeddings.json"))

        # nodes_load = json.load(open(f_saved + "/nodes.json"))
        # for count in range(len(nodes_load.keys())): 
        #     node_id = f"node_{str(count+1)}"
        #     node_details = nodes_load[node_id]

        #     node_count = node_details["node_count"]
        #     type_count = node_details["type_count"]
        #     node_type = node_details["type"]
        #     depth = node_details["depth"]

        #     created = datetime.datetime.strptime(node_details["created"], 
        #                                         '%Y-%m-%d %H:%M:%S')
        #     expiration = None
        #     if node_details["expiration"]: 
        #         expiration = datetime.datetime.strptime(node_details["expiration"],
        #                                                 '%Y-%m-%d %H:%M:%S')

        #     s = node_details["subject"]
        #     p = node_details["predicate"]
        #     o = node_details["object"]

        #     description = node_details["description"]
        #     embedding_pair = (node_details["embedding_key"], 
        #                         self.embeddings[node_details["embedding_key"]])
        #     poignancy =node_details["poignancy"]
        #     keywords = set(node_details["keywords"])
        #     filling = node_details["filling"]
            
        #     if node_type == "action": 
        #         self.add_event(created, expiration, s, p, o, 
        #                 description, keywords, poignancy, embedding_pair, filling)
        #     elif node_type == "chat": 
        #         self.add_chat(created, expiration, s, p, o, 
        #                 description, keywords, poignancy, embedding_pair, filling)
        #     elif node_type == "thought": 
        #         self.add_thought(created, expiration, s, p, o, 
        #                 description, keywords, poignancy, embedding_pair, filling)

        # kw_strength_load = json.load(open(f_saved + "/kw_strength.json"))
        # if kw_strength_load["kw_strength_event"]: 
        #     self.kw_strength_event = kw_strength_load["kw_strength_event"]
        # if kw_strength_load["kw_strength_thought"]: 
        #     self.kw_strength_thought = kw_strength_load["kw_strength_thought"]

    def add_thought(self):
        pass

    def add_reverie(self):
        pass

    def add_action(self):
        pass

    def add_chat(self): 
        pass


    def get_summarized_latest_events(self, retention): 
        ret_set = set()
        [ret_set.add(e_node.spo_summary()) for e_node in self.seq_event[:retention]]
        return ret_set


    def get_str_seq_events(self): 
        return "".join([f'{"Event", len(self.seq_event) - count, ": ", event.spo_summary(), " -- ", event.description}\n' for count, event in enumerate(self.seq_event)])

    def get_str_seq_thoughts(self): 
        return "".join([f'{"Thought", len(self.seq_thought) - count, ": ", event.spo_summary(), " -- ", event.description}' for count, event in enumerate(self.seq_thought)])

    def retrieve_relevant_thoughts(self, subj_content, pred_content, obj_content): 
        contents = [subj_content, pred_content, obj_content]

        ret = []
        for i in contents: 
            if i in self.kw_to_thought: 
                ret += self.kw_to_thought[i.lower()]
        
        ret = set(ret)
        return ret

    def retrieve_relevant_events(self, s_content, p_content, o_content): 
        contents = [s_content, p_content, o_content]

        ret = []
        for i in contents: 
            if i in self.kw_to_event: 
                ret += self.kw_to_event[i]

        ret = set(ret)
        return ret

    def save_to_file(self, file_path: str):
        pass