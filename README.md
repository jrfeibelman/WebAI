# WebAI

## RTAI:

### Setup:

- Note: All code should be run from the WebAI directory level

1) Copy .env.example to .env and add your own keys

2) Add rtai dir to python path:
    export PYTHONPATH="${PYTHONPATH}:./rtai"

4) Then, spin up the LMStudio inference server. Make sure to enable Metal acceleration and to allow Request Queuing.

5) `python3 rtai/main.py`

### Architecture Notes

### llm
For llm, there is an `LLMClient` that interfaces with the local llm model, hosted on a server. Currently, we use LM Studio which spins up a server for inference. 

The prompt logic is in `llm/prompt.py`. Currently, there is a reverie_prompt for creating a reverie based off the persona of the agent.

One thing to think about is what is assosciated with the agent and what is assosciated with the LLMClient.

### TODOs
* clarify when a thought should be done 
    * in the paper, this is done with <- can this be done without the environment? probably...

-----
Jason TODO
1) Chat functionality **** add chat to 2 agents daily schedule
    - don't add new fu
    - What does it look like when agents interact?
2) Simulated world
    - if agents are not in the same room, they cannot interact
    - DAG map of locations, each with a name and description
---------------------
2) Reflection functionality
4) Creating thoughts

