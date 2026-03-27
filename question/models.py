import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

gemini_model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={"temperature": 0.0}
)


def generate_answer(question, context):
    prompt = f"""
Answer the question using ONLY the provided context.

Rules:
- Do NOT use outside knowledge
- Keep the answer short and precise
- You MAY rephrase slightly for clarity
- Do NOT add extra information

Context:
{context}

Question:
{question}

Answer:
"""

    response = gemini_model.generate_content(prompt)

    return response.text.strip()


def get_embedding(text):
    response = genai.embed_content(
        model="gemini-embedding-001",
        content=text
    )
    return response["embedding"]
