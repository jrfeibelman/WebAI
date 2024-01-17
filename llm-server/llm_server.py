from fastapi import FastAPI
from guidance import models, gen
import guidance
from prompts import create_daily_tasks
from pydantic import BaseModel

mistral = models.LlamaCpp("/Users/nyeung/Projects/llama.cpp/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf", n_context=2048, caching=False)
mistral.echo = False


class Request(BaseModel):
    prompt: str

app = FastAPI()

@app.post("/")
def generate(request: Request):
    lm = mistral + request.prompt
    out = lm + create_daily_tasks()
    tasks = out["tasks"]
    return tasks[0]