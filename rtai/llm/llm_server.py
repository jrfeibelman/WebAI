'''
Fast API scaffolding for a local server for model
'''

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai

app = FastAPI()

# Set your OpenAI API key
openai.api_key = "your_openai_api_key_here"

class Prompt(BaseModel):
    text: str

@app.post("/complete/")
async def complete(prompt: Prompt):
    try:
        # Use the OpenAI API to generate a completion
        response = openai.Completion.create(
            engine="text-davinci-003",  # Adjust the engine based on your needs
            prompt=prompt.text,
            max_tokens=50  # Adjust the max_tokens based on your needs
        )
        return {"completion": response.choices[0].text.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")
