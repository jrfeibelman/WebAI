from typing import List
from dataclasses import dataclass, fields

@dataclass
class Persona:
    first_name: str
    last_name: str
    name: str
    occupation: str
    backstory: str
    hobbies: str
    traits: str
    motivations: str
    relationships: List[str]

    # location: str
    # action: str
    # action_desc: str
    # action_duration: str
    # action_start: str
    # action_location: str

    def get_name(self) -> str:
        return "%s [%s]" % (self.name, self.occupation)

    @classmethod
    def generate(cls):
        e =  cls.__new__(cls)
        # TODO populate fields of e with LLM
        return e

    @classmethod
    def generate_from_file(cls, file_path: str):
        e =  cls.__new__(cls)
        data = dict()
        with open(file_path, "r") as f:
            for line in f.readlines():
                split = line.split(": ")
                val = split[1].strip() if len(split) > 1 else ""
                data[split[0]] = val
        
        e = Persona(**data)
        return e
    
    # def _class_from_dict(self, argDict: dict):
    #     fieldSet = {f.name for f in fields(Persona) if f.init}
    #     filteredArgDict = {k : v for k, v in argDict.items() if k in fieldSet}
    #     print(filteredArgDict)
    #     return Persona(**filteredArgDict)

