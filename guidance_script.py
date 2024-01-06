from guidance import models, instruction, gen
import guidance

def generate_prompt():
    # persona + common strings
    name1 = "Hank Thompson"
    persona1 = "Hank Thompson, 54 years old, farmer, born and raised in a small town in Iowa, inherited family farm, continues the agricultural tradition with pride, enjoys tractor rides and classic country music, looks forward to local county fairs, likes hearty, home-cooked meals, dislikes city life, does not like genetically modified crops, pests and weeds"

    name2 = "Claire Reynolds"
    persona2 = "Claire Reynolds, 50 years old, agronomist, grew up in a suburban area, likes sustainable agriculture and rural life"

    # location
    location = "barn in Iowa"

    # relationships
    persona1topersona2 = "Hank admires Claire over their shared values"
    persona2topersona1 = "Claire echoes Hank's aversion to city life, can relate to Hank's love for the countryside"

    prompt = f"""
    Generate a short dialogue between {name1} and {name2} in {location}

    {name1} context: {persona1} {persona1topersona2}
    {name2} context: {persona2} {persona2topersona1}

    Example of dialogue:
    Hank: Howdy, Claire, how's it going?
    Claire: Good, what about you?

    Here is the short dialogue:
    {gen('dialogue', max_tokens=1000)}"""

    out3 = mistral + prompt