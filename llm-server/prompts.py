import guidance
from guidance import gen

# TODO: create a function that maps a task to a prompt
def task_to_prompt(task, args):
    if task == "dialogue":
        return create_daily_tasks(args)

@guidance
def generate_dialogue_about_topic(lm, dialogue_topic, location):
    lm += f"""
    Generate a short dialogue between Isabella Martinez and Claire Reynolds in {location} about {dialogue_topic}

    Example of dialogue:
    Isabella: Hey, Claire, how's it going?
    Claire: Good, what about you?

    Here is the short dialogue:
    Isabella: {gen(name='dialogue1', max_tokens=100)}
    Claire: {gen(name='dialogue2', max_tokens=100)}
    Isabella: {gen(name='dialogue3', max_tokens=100)}
    Claire: {gen(name='dialogue4', max_tokens=100)}
    """
    return lm

# def generate_dialogue(lm, persona1, persona2, location):
#     lm += f"""
#     Generate a short dialogue between {persona1.name} and {persona2.name} in {location}

#     {persona1.name} context: {persona1.common_str} {persona1.relationships[persona2.name]}
#     {persona2.name} context: {persona2.common_str} {persona2.relationships[persona1.name]}

#     Example of dialogue:
#     Isabella: Howdy, Claire, how's it going?
#     Claire: Good, what about you?

#     Here is the short dialogue:
#     {gen('dialogue', max_tokens=1000)}"""
#     return lm

@guidance
def create_daily_tasks(lm, num_tasks=2):
    for i in range(num_tasks):
        print("doing task", i)
        lm += f'''Briefly describe a task {i+1} that a ceo does in a day in 10 or less words: "{gen(stop=".", name="tasks", temperature=1.0, list_append=True)}"\n'''
    return lm

'''
We feed in the most recent information and then generate 3 questions that we can ask about the information
'''
@guidance
def generate_questions(lm, context):
    lm += f'''
    {context}

    Given only the information above, what are 3 most salient high-level questions we can answer about the subjects in the statements?
    Question 1: {gen(stop="?", name="q1", temperature=1.0)}
    Question 2: {gen(stop="?", name="q2", temperature=1.0)}
    Question 3: {gen(stop="?", name="q3", temperature=1.0)}
    '''
    return lm

@guidance
def generate_insights(lm, questions):
    lm += f'''
    Questions: {questions}
    Create 5 insights that can be derived from the questions above.
    Insight 1: {gen(stop=".", name="insight1", temperature=1.0)}
    Insight 2: {gen(stop=".", name="insight2", temperature=1.0)}
    Insight 3: {gen(stop=".", name="insight3", temperature=1.0)}
    Insight 4: {gen(stop=".", name="insight4", temperature=1.0)}
    Insight 5: {gen(stop=".", name="insight5", temperature=1.0)}
    '''
    return lm