
from PIL import Image

import torch

from transformers import (
    CLIPModel,
    CLIPProcessor
)


model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)

model.eval()


def generate_embedding(image):

    if isinstance(image, str):

        image = Image.open(image).convert("RGB")

    else:

        image = image.convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():

        image_features = model.get_image_features(**inputs)

    image_features = image_features / (image_features.norm(dim=-1,keepdim=True))

    embedding = (
        image_features
        .cpu()
        .numpy()
        .flatten()
    )

    return embedding