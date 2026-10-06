import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
)


response = client.chat.completions.create(
    model="z-ai/glm-5-3",
    messages=[
        {
            "role": "user",
            "content": "Say hello in one sentence."
        }
    ],
)


print(response.choices[0].message.content)