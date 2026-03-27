import numpy as np
from models import get_embedding
from docx import Document
from PyPDF2 import PdfReader
import csv
import re


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return text

    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return " ".join([para.text for para in doc.paragraphs])

    elif file_path.endswith(".csv"):
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            return " ".join([" ".join(row) for row in reader])

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError("Unsupported file format")

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def enhance_query(query):
    return f"Explain clearly: {query}"

def retrieve_top_k(query, vector_store, k=3):
    query_embedding = get_embedding(enhance_query(query))

    scores = []

    for item in vector_store:
        score = cosine_similarity(query_embedding, item["embedding"])

        score -= len(item["text"]) * 0.00001

        scores.append((score, item["text"]))

    scores.sort(key=lambda x: x[0], reverse=True)

    return scores[:k]