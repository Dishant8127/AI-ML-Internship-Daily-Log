# import numpy as np
from transformers import CLIPProcessor, CLIPModel




model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)
processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)



# def normalize_embeddings(embeddings):
#     norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
#     return embeddings / norms