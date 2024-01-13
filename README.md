# Mythos AI:

Imagine a world where you can bring your wildest imagination to life, where you are not just a passive reader but the mastermind behind the narrative. With our platform, you can create your own unique story simulations. Start with a base game, where the actions and objects are predefined, and then let your creativity run wild.

🌍 Customize the world: Craft imaginary realms, futuristic cities, or enchanted forests. The power to shape your story's setting is in your hands.

👥 Personalize characters: Design heroes, villains, and everything in between. Define their personalities, motivations, and quirks to breathe life into your tale.

📜 Shape the plot: From thrilling adventures to mysterious whodunits, you decide the story's direction. No two simulations will ever be the same.

🎮 Interactive control: Dive into the simulation as a character, or watch from a birds-eye view. Real-time, hands-on control allows you to steer the story in any direction you desire.

📖 Experience the narrative: Sit back and enjoy the overarching story that unfolds from your simulation, with surprises at every turn.

Unlock your storytelling potential and create immersive, customizable worlds and narratives like never before. The Story Simulation Engine is your canvas, and the story is your masterpiece. Are you ready to rewrite the future of storytelling? 📚✨

## Setup:

- Note: All code should be run from the WebAI directory level

1) Copy .env.example to .env and add your own keys

2) Add rtai dir to python path:
    export PYTHONPATH="${PYTHONPATH}:./rtai"

4) Then, spin up the LMStudio inference server. Make sure to enable Metal acceleration and to allow Request Queuing.

5) `python3 rtai/main.py`

## Architecture Notes

### llm
For llm, there is an `LLMClient` that interfaces with the local llm model, hosted on a server. Currently, we use LM Studio which spins up a server for inference. 

The prompt logic is in `llm/prompt.py`. Currently, there is a reverie_prompt for creating a reverie based off the persona of the agent.

One thing to think about is what is assosciated with the agent and what is assosciated with the LLMClient.

Need to move away from LMStudio server so can have more control...but might need to be OpenAI API compliant to use any libraries.

### llama-cpp
To download local model.

`pip3 install huggingface-hub`

`huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF mistral-7b-instruct-v0.2.Q4_K_M.gguf --local-dir . --local-dir-use-symlinks False
`

### TODOs
* clarify when a thought should be done 
    * in the paper, this is done with <- can this be done without the environment? probably...

-----------------------------------------------------------------------

### Architecture
##### Agents
- All agents have access to the shared AgentManager object, World object, and Clock object
- All cross agent interaction should be managed by AgentManager
- All agents should run in their own thread
- All agents can receive events from AgentManager (narration, other agent request, world change, new day, etc)
    - Thus they need to poll an internal queue to process events if there are any
- All agents dispatch events (actions, chats) to AgentManager, which puts it onto worker queue (for World)
- To chat, one agent initiates a request, and the other accepts. Then AgentManager creates shared conversation data structure
    to maintain chat history used for prompting. When chat is completed, it's summarized and put into memory
- All LLM functionality for a given agent should be done in separate thread to not block agent from updating its state and waiting

##### Memory
- Shared memory includes world, clock, and agent manager objects. Otherwise all agents should have own memory


### Identified Issues:
- How should agent update as world clock updates? 
  - If world clock increments by a minute every 1 second, shouldn't the agent also update itself at least once every second
    - Otherwise it can end or start an action not at the proper time
    - Not feasible if LLM calls can take in the magnitude of seconds
  - Maybe all LLM calls for an agent are wrapped in a function, which is called in a separate thread to not block agent update! 
    - What could it be blocking?
        - Changing actions and starting a new one when current one ends 
        - Receving chat requests from other agents
- *** There must be a max speed enforced on world clock based on WorldClockScaleMs and AgentTimerMillis.
    - Maybe add config to synchronize world clock with agent updating to speed up running simulation for test purposes
    - This way, first world clock updates, then agent updates. Will be faster bc on most iters agent update is very fast