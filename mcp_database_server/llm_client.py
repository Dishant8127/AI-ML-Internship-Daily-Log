import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    raise ValueError(
        "NVIDIA_API_KEY is missing from .env"
    )


client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY,
)


# MODEL = "meta/llama-3.1-70b-instruct"
MODEL = "z-ai/glm5"


def ask_nvidia(messages, tools):

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2,
        max_tokens=1000,
    )

    return response