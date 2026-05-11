import os
import json
import torch

import numpy as np

from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from model import model, processor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMBEDDING_PATH = os.path.join(BASE_DIR, "embeddings.json")

with open(EMBEDDING_PATH, "r") as f:
    stored_embeddings = json.load(f)


def search_similar_image(query_image_path):

    image = Image.open(query_image_path).convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():
        query_embedding = model.get_image_features(
            **inputs
        )

    query_embedding = query_embedding / query_embedding.norm(dim=-1, keepdim=True)

    query_embedding = query_embedding.cpu().numpy()

    similarities = []

    for item in stored_embeddings:

        stored_embedding = np.array(item["embedding"]).reshape(1, -1)

        similarity = np.dot(query_embedding,stored_embedding.T)[0][0]

        similarities.append({
            "category": item.get("category", "Unknown"),
            "image_name": item["image_name"],
            "image_path": item["image_path"],
            "similarity": float(similarity)
        })

    similarities = sorted(
        similarities,
        key=lambda x: x["similarity"],
        reverse=True
    )

    return similarities[:3]