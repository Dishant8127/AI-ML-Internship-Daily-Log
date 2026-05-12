from sklearn.cluster import KMeans

import faiss

def cluster_embeddings(embeddings, n_clusters=10):

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype("float32"))

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    labels = kmeans.fit_predict(embeddings)

    return labels, index