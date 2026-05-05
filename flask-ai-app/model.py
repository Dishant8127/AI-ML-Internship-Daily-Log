import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_text(prompt):
    try:
        full_prompt = f"""
Generate a clear and meaningful response for the following prompt.

Rules:
- Maximum 300 words
- Keep it informative and relevant
- Avoid unnecessary repetition

Prompt:
"""
{prompt}

        response = model.generate_content(full_prompt)
        return response.text.strip()

    except Exception as e:
        return str(e)
    



    

def summarize_text(text):
    try:
        prompt = f"""
Summarize the text in EXACTLY ONE short sentence.

Rules:
- Maximum 15 words
- No extra details
- No examples
- Only core idea

Text:
{text}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return str(e)