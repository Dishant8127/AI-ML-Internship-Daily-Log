import os
import cv2
import numpy as np
import pandas as pd

from src.preprocess import enhance_image
from src.embedding import generate_embedding
from src.similarity import cosine_similarity_score , save_comparison_image

INPUT_DIR = "data/input"
PROCESSED_DIR = "data/processed"
COMPARISON_DIR = "data/comparison"
REPORT_PATH = "data/reports/similarity_report.csv"


results = []

for image_name in os.listdir(INPUT_DIR):

    image_path = os.path.join(INPUT_DIR, image_name)

    before_img = cv2.imread(image_path)

    if before_img is None:
        continue

    after_img = enhance_image(image_path)

    after_path = os.path.join(PROCESSED_DIR, image_name)

    cv2.imwrite(after_path, after_img)

    comparison_path = os.path.join(COMPARISON_DIR, image_name)
    save_comparison_image(before_img, after_img, comparison_path)

    before_embedding = generate_embedding(image_path)
    after_embedding = generate_embedding(after_path)

    similarity = cosine_similarity_score(before_embedding,after_embedding)

    results.append({
        "image_name": image_name,
        "similarity_score": similarity
    })

    print(f"{image_name} -> Similarity: {similarity:.4f}")

df = pd.DataFrame(results)
df.to_csv(REPORT_PATH, index=False)
