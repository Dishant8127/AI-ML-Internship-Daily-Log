
vector_store = []

def add_to_store(text, embedding):
    vector_store.append({
        "text": text,
        "embedding": embedding
    })

def get_store():
    return vector_store