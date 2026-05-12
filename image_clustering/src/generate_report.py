import pandas as pd
import json
import os
from collections import defaultdict

def generate_reports(image_paths, labels):

    cluster_data = defaultdict(list)

    for path, label in zip(image_paths, labels):
        cluster_data[int(label)].append(path)

    rows = []

    json_output = []

    for cluster_id, images in cluster_data.items():

        sample_images = images[:5]

        rows.append({
            "cluster_id": cluster_id,
            "num_images": len(images),
            "sample_images": ", ".join(sample_images)
        })

        json_output.append({
            "cluster_id": cluster_id,
            "num_images": len(images),
            "sample_images": sample_images,
            "all_images": images
        })

    df = pd.DataFrame(rows)

    os.makedirs("outputs", exist_ok=True)

    df.to_csv("outputs/clusters.csv", index=False)

    with open("outputs/clusters.json", "w") as f:
        json.dump(json_output, f, indent=4)
