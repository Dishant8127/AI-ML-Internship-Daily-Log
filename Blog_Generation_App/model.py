from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="gpt2"
)


def generate_text(text):
    result = generator(
        text,          
        max_length=200,      
        temperature=1.0,
        top_p=0.9,
        num_return_sequences=1
    )
    return result[0]['generated_text'] 