from transformers import pipeline

qa = pipeline("question-answering")

context = """
Hugging Face develops tools for building machine learning applications using transformers.
"""

question = "What does Hugging Face develop?"

result = qa(question=question, context=context)

print(result)



# from transformers import pipeline

# qa = pipeline(
#     model="distilbert-base-cased-distilled-squad"
# )

# context = """
# Hugging Face develops tools for building machine learning applications using transformers.
# """

# question = "What does Hugging Face develop?"

# result = qa(question=question, context=context)

# print(result["answer"])