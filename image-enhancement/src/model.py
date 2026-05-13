
from transformers import CLIPProcessor, CLIPVisionModel


model = CLIPVisionModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)




