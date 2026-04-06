import os
import requests

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"


def call_nvidia_api(text, task="generate"):

    if task == "summarize":
        prompt = f"Summarize this:\n{text}"
    elif task == "generate":
        prompt = text
    else:
        prompt = text

    payload = {
        "model": "meta/llama3-70b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(NVIDIA_API_URL, json=payload, headers=headers)
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return {"error": str(e)}