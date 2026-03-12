# from transformers import pipeline

# tc = pipeline("text-classification")

# text = tc("Congratulations! You won $1000. Click this link now!")

# print(text)


from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="unitary/unbiased-toxic-roberta"
)

print(classifier("You won $1000! Click here now"))