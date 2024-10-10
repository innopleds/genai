from fastapi import FastAPI, HTTPException
import requests
import openai
import json
import base64
import os
from pydantic import BaseModel
import os

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    image_url: str


def url_to_base64(image_url):
    response = requests.get(image_url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Image not found")
    img_base64 = base64.b64encode(response.content).decode("utf-8")
    return img_base64


def get_openai_response(query, base64_image):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    url = "https://api.openai.com/v1/chat/completions"
    model = "gpt-4o"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.4
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from OpenAI")

    return response.json()


@app.post("/generate")
def generate_prompt(request: QueryRequest):
    try:

        base64_image = url_to_base64(request.image_url)

     
        response_data = get_openai_response(request.query, base64_image)

  
        content = response_data['choices'][0]['message']['content']

        return {"result": content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# uvicorn prompt:app --reload
