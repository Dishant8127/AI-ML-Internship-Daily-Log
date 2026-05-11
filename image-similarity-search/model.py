# import open_clip

# model, _, preprocess = open_clip.create_model_and_transforms(
#     'ViT-B-32',
#     pretrained='laion2b_s34b_b79k'
# )


from transformers import CLIPModel, CLIPProcessor

# Load CLIP model
model = CLIPModel.from_pretrained(
    "openai/clip-vit-base-patch32"
)

# Load CLIP processor
processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32"
)