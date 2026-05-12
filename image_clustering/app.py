import os
import json
import numpy as np

from src.model import get_image_paths
from src.extract_embeddings import generate_embeddings
from src.cluster_images import cluster_embeddings
from src.generate_report import generate_reports
from src.visualize_clusters import visualize_clusters

DATASET_FOLDER = "dataset"
N_CLUSTERS = 10

def main():


    image_paths = get_image_paths(DATASET_FOLDER)

    embeddings = generate_embeddings(image_paths)


    np.save("outputs/embeddings.npy", embeddings)

    with open("outputs/image_paths.json", "w") as f:
        json.dump(image_paths, f)


    labels, index = cluster_embeddings( embeddings,n_clusters=N_CLUSTERS)


    generate_reports(image_paths, labels)


    visualize_clusters(embeddings, labels)

if __name__ == "__main__":
    main()