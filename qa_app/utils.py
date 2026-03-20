import os
import pickle
import numpy as np
from PyPDF2 import PdfReader
from model import embedding_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "data", "embeddings.pkl")


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        return text

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    return ""

def chunk_text(text, chunk_size=100):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks


def save_embeddings(data):
    os.makedirs(os.path.dirname(EMBEDDINGS_FILE), exist_ok=True)

    with open(EMBEDDINGS_FILE, "wb") as f:
        pickle.dump(data, f)


def load_embeddings():
    if os.path.exists(EMBEDDINGS_FILE):
        with open(EMBEDDINGS_FILE, "rb") as f:
            return pickle.load(f)
    return []


def add_document(file_path):
    text = extract_text(file_path)

    if not text.strip():
        return

    chunks = chunk_text(text)

    if len(chunks) == 0:
        return

    embeddings_data = load_embeddings()

    for chunk in chunks:
        emb = embedding_model.encode(chunk)

        embeddings_data.append({
            "text": chunk,
            "embedding": emb,
            "source": os.path.basename(file_path)
        })

    save_embeddings(embeddings_data)

def search(query, top_k=3):
    embeddings_data = load_embeddings()

    if not embeddings_data:
        return []

    query_emb = embedding_model.encode(query)

    scores = []
    for item in embeddings_data:
        score = np.dot(query_emb, item["embedding"])
        scores.append((score, item))

    scores = sorted(scores, key=lambda x: x[0], reverse=True)

    return scores[:top_k]