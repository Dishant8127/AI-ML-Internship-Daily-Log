from transformers import pipeline

sentiment = pipeline("sentiment-analysis")

result = sentiment("This product is terrible and waste of money")

print(result)