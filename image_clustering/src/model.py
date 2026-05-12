import torch
import os
from transformers import CLIPModel, CLIPProcessor


model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

model.eval()






IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

def get_image_paths(folder):
    paths = []

    for file in os.listdir(folder):
        if file.lower().endswith(IMAGE_EXTENSIONS):
            paths.append(os.path.join(folder, file))

    return paths