
import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

pc = Pinecone(api_key=PINECONE_API_KEY)

index = pc.Index("rag-langchain")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


llm = genai.GenerativeModel("gemini-2.5-flash")