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

Need to move away from LMStudio server so can have more control...but might need to be OpenAI API compliant to use any libraries

### TODOs
* clarify when a thought should be done 
    * in the paper, this is done with <- can this be done without the environment? probably...