from typing import List
from dataclasses import dataclass, fields
from numpy import uint8
@dataclass
class Persona:
    """_summary_ Class to represent a the personality of an agent."""

    first_name: str
    last_name: str
    name: str
    occupation: str
    backstory: str
    hobbies: str
    traits: str
    motivations: str
    relationships: List[str]
    age: uint8

    # location: str
    # action: str
    # action_desc: str
    # action_duration: str
    # action_start: str
    # action_location: str

    def get_name(self) -> str:
        """_summary_ Get the name of the agent's persona.

        Returns:
            str: The name of the agent's persona.
        """
        return self.name

    @classmethod
    def generate(cls) -> "Persona":
        """_summary_ Generate a persona using LLM and randomization

        Returns:
            Persona: A persona object.
        """
        e =  cls.__new__(cls)
        # TODO populate fields of e with LLM
        return e

    @classmethod
    def generate_from_file(cls, file_path: str) -> "Persona":
        """_summary_ Generate a persona from a file.

        Args:
            file_path (str): Path to the file containing the persona data.
        Returns:
            Persona: A persona object.
        """
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

