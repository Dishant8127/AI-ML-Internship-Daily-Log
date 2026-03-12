from transformers import pipeline

tg  = pipeline("text-generation", model="gpt2")

result = tg("Artificial Intelligence is", max_length=30)

print(result)