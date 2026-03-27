import numpy as np 
from models import get_embedding
import os
import pandas as pd
from docx import Document
from PyPDF2 import PdfReader
import csv


def extract_text(file_path):
    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + " "
        return text.strip()
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        text = " ".join([para.text for para in doc.paragraphs])
        return text.strip()
    elif file_path.endswith(".csv"):
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            text = " ".join([" ".join(row) for row in reader])
            return text.strip()
        
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    else:
        raise ValueError("Unsupported file format")

def chunk_text(text , chunk_size = 300):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_top_k(query, vector_store, k=3):
    query_embedding = get_embedding(query)
    scores = []
    for item in vector_store:
        score = cosine_similarity(query_embedding, item["embedding"])
        scores.append((score, item["text"]))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[:k]


 