import json
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity


with open(
    "embeddings/embeddings.json",
    "r"
) as f:

    database = json.load(f)


def search_similar(
    query_embedding,
    top_n=5
):

    results = []

    for item in database:

        db_embedding = np.array(
            item["embedding"]
        )

        similarity = cosine_similarity(
            [query_embedding],
            [db_embedding]
        )[0][0]

        results.append({
            "filename": item["filename"],
            "similarity": float(similarity),
            "metadata": item["metadata"]
        })

    results = sorted(
        results,
        key=lambda x: x["similarity"],
        reverse=True
    )

    return results[:top_n]