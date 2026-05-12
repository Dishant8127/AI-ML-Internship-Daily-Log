import numpy as np
import torch
from PIL import Image
from tqdm import tqdm
from src.model import model , processor

def generate_embeddings(image_paths):

    embeddings = []

    for path in tqdm(image_paths):

        try:
            image = Image.open(path).convert("RGB")

            inputs = processor(
                images=image,
                return_tensors="pt"
            )

            with torch.no_grad():

                image_features = model.get_image_features(**inputs)

            embedding = image_features.numpy()[0]

            embedding = embedding / np.linalg.norm(embedding)

            embeddings.append(embedding)

        except Exception as e:

            print(f"Error processing {path}: {e}")

    return np.array(embeddings)