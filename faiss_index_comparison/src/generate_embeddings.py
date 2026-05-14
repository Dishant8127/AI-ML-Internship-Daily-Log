import os
import numpy as np
from PIL import Image
from tqdm import tqdm

import torch
from model import processor , model



IMAGE_FOLDER = "data/images"

SAVE_PATH = "data/embeddings.npy"

IMAGE_NAMES_PATH = "data/image_names.npy"


SUPPORTED_EXTENSIONS = (".jpg",".jpeg",".png")


image_files = [
    file for file in os.listdir(IMAGE_FOLDER)
    if file.lower().endswith(SUPPORTED_EXTENSIONS)
]



embeddings = []

image_names = []


for img_name in tqdm(image_files):

    try:

        path = os.path.join(IMAGE_FOLDER, img_name)

        image = Image.open(path).convert("RGB")


        inputs = processor(images=image,return_tensors="pt")

        pixel_values = inputs["pixel_values"]


        with torch.no_grad():

            outputs = model.vision_model(pixel_values=pixel_values)

            pooled_output = outputs.pooler_output


        pooled_output = pooled_output / torch.norm(pooled_output,dim=-1,keepdim=True)


        embedding = (pooled_output.cpu().numpy()[0].astype("float32"))

        embeddings.append(embedding)

        image_names.append(img_name)

    except Exception as e:

        print(f"\nError processing {img_name}")

        print("Reason:", e)


print(f"\nSuccessful Embeddings: {len(embeddings)}")

if len(embeddings) == 0:

    raise ValueError("No embeddings generated.")

embeddings = np.array(embeddings,dtype="float32")



np.save(SAVE_PATH,embeddings)

np.save(IMAGE_NAMES_PATH,np.array(image_names))
