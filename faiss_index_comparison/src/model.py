from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)
processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)
