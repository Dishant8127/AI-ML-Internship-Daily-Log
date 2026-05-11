import os
import json
import torch

from PIL import Image
from model import model, processor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_FOLDER = os.path.join(BASE_DIR, "images")

embeddings_data = []

for category in os.listdir(IMAGE_FOLDER):

    category_path = os.path.join(IMAGE_FOLDER, category)

    if not os.path.isdir(category_path):
        continue

    for image_name in os.listdir(category_path):

        image_path = os.path.join(category_path, image_name)

        try:
            image = Image.open(image_path).convert("RGB")

            inputs = processor(
                images=image,
                return_tensors="pt"
            )

            with torch.no_grad():
                embedding = model.get_image_features(
                    **inputs
                )

            embedding = embedding / embedding.norm(dim=-1, keepdim=True)

            embeddings_data.append({
                "category": category,
                "image_name": image_name,
                "image_path": image_path,
                "embedding": embedding[0].cpu().numpy().tolist()
            })

            print(f"Processed: {category}/{image_name}")

        except Exception as e:
            print(f"Error processing {image_name}: {e}")

embedding_file = os.path.join(BASE_DIR, "embeddings.json")

with open(embedding_file, "w") as f:
    json.dump(embeddings_data, f)
