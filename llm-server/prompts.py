import guidance
from guidance import gen

@guidance
def create_daily_tasks(lm, num_tasks=2):
    for i in range(num_tasks):
        print("doing task", i)
        lm += f'''Briefly describe a task {i+1} that a ceo does in a day in 10 or less words: "{gen(stop=".", name="tasks", temperature=1.0, list_append=True)}"\n'''
    return lm