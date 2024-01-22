from fastapi import FastAPI
from guidance import models
from prompts import generate_dialogue_about_topic
from pydantic import BaseModel
from typing import Dict, Any

mistral = models.LlamaCpp("/Users/nyeung/Projects/llama.cpp/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf", n_context=2048, caching=True)
mistral.echo = False

class Request(BaseModel):
    prompt: str
    task: str
    args: Dict[str, Any]

app = FastAPI()

@app.post("/")
def generate(request: Request):
    lm = mistral + request.prompt # story telling prompt
    dialogue_topic, location = request.args["dialogue_topic"], request.args["location"]
    out = lm + generate_dialogue_about_topic(dialogue_topic, location)
    out1, out2, out3, out4 = out["dialogue1"], out["dialogue2"], out["dialogue3"], out["dialogue4"]
    lm.reset()
    return out1 + out2 + out3 + out4