import pickle
import os
from PyPDF2 import PdfReader
import csv
from models import embedding_model 
import numpy as np

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
    elif file_path.endswith(".csv"):
        text = ""
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                text += " ".join(row) + "\n"
        return text
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

    embeddings = load_embeddings()
    new_embeddings = embedding_model.encode(chunks)
    for chunk, emb in zip(chunks, new_embeddings):
        embeddings.append({
            "text": chunk,
            "embedding": emb,
            "source": file_path
        })
    save_embeddings(embeddings)


def search(query, top_k=3):
    embeddings = load_embeddings()
    if not embeddings:
        return []

    query_emb = embedding_model.encode([query])[0]

    results = []

    for item in embeddings:
        score = np.dot(query_emb, item["embedding"])
        results.append((score, item))

    sorted_items = sorted(results, key=lambda x: x[0], reverse=True)

    return sorted_items[:top_k]