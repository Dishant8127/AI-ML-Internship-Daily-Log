import torch
from PIL import Image
from src.model import model , processor


def generate_embedding(image_path):

    image = Image.open(image_path).convert("RGB")

    inputs = processor(images=image,return_tensors="pt")

    with torch.no_grad():

        outputs = model(pixel_values=inputs["pixel_values"])

        embedding = outputs.pooler_output

    embedding = torch.nn.functional.normalize(embedding,p=2,dim=-1)

    return embedding.squeeze().cpu().numpy()