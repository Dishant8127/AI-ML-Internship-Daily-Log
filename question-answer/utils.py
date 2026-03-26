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
        text = "".join([p.extract_text() or "" for p in reader.pages])
        return text
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif file_path.endswith(".csv"):
        text = ""
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                text += " ".join(row) + "\n"
        return text
    return ""


def chunk_text(text, chunk_size=1000):
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return [c for c in chunks if c.strip()]


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
    embeddings = load_embeddings()
    new_embeddings = embedding_model.encode(chunks)
    for chunk, emb in zip(chunks, new_embeddings):
        embeddings.append({
            "text": chunk,
            "embedding": emb,
            "source": file_path
        })
    save_embeddings(embeddings)


def cosine_similarity(a, b):
    a = np.array(a).flatten()
    b = np.array(b).flatten()

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def search(query, top_k=3):
    embeddings = load_embeddings()
    if not embeddings:
        return []

    query_emb = embedding_model.encode([query])[0]
    results = []

    for item in embeddings:
        if len(query_emb) != len(item["embedding"]):
            continue
        score = cosine_similarity(query_emb, item["embedding"])
        results.append((score, item))

    results = sorted(results, key=lambda x: x[0], reverse=True)
    return results[:top_k]  

def score_answer(answer, context):
    if not answer.strip() or not context.strip():
        return 0.0

    emb1 = embedding_model.encode([answer])[0]
    emb2 = embedding_model.encode([context])[0]
    score = cosine_similarity(emb1, emb2)
    return float(score)