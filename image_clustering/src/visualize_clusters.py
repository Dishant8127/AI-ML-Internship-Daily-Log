import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np

def visualize_clusters(embeddings, labels):

    pca = PCA(n_components=2)

    reduced = pca.fit_transform(embeddings)

    plt.figure(figsize=(12, 8))

    scatter = plt.scatter(
        reduced[:, 0],
        reduced[:, 1],
        c=labels,
        cmap='tab20'
    )

    plt.colorbar(scatter)

    plt.title("Image Cluster Visualization")

    plt.savefig("outputs/cluster_visualization.png")
