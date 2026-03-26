from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

gemini_model = genai.GenerativeModel("gemini-2.5-flash")


# def generate_answer(question, context):
#     prompt = f"""
#     Answer ONLY from the given context. If the answer is not in the context, say "I don't know".

#     Context:
#     {context}

#     Question:
#     {question}

#     Answer:
#     """

#     response = gemini_model.generate_content(prompt)

#     return response.text


from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_answer(question, context):
    prompt = f"""  Answer ONLY from the given context. If the answer is not in the context, say "I don't know".

    Context:
    {context}

    Question:
    {question}  

    Answer:
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    return response.text
