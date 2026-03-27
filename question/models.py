import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key = os.getenv("GEMINI_API_KEY"))

gemini_model = genai.GenerativeModel("gemini-2.5-flash")

def generate_answer(question, context):
    prompt = f"""
    Extract the exact answer from the context.

    Do NOT explain.
    Do NOT add examples.
    Do NOT add extra sentences.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    response = gemini_model.generate_content(prompt)

    return response.text    

def get_embedding(text):
    response = genai.embed_content(model = "gemini-embedding-001" , content = text )
    return response["embedding"]
