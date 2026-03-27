
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from utils import chunk_text, extract_text, retrieve_top_k, clean_text
from models import get_embedding, generate_answer
from vector_store import add_to_store, get_store

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "data/docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")

    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        raw_text = extract_text(path)
        text = clean_text(raw_text)

        chunks = chunk_text(text)

        for chunk in chunks:
            embedding = get_embedding(chunk)
            add_to_store(chunk, embedding)

    return jsonify({"message": "Files processed successfully"})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")

    print("\nQuery:", question)

    store = get_store()

    if not store:
        return jsonify({"answer": "No documents uploaded yet."})

    top_chunks = retrieve_top_k(question, store, k=3)

    print("\n===== Top Retrieved Chunks =====")
    for i, (score, chunk) in enumerate(top_chunks, 1):
        print(f"\nRank {i}")
        print(f"Score: {score}")
        print(f"Chunk: {chunk[:200]}")

    best_chunk = top_chunks[0][1]
    best_score = top_chunks[0][0]

    answer = generate_answer(question, best_chunk)

    return jsonify({
        "answer": answer,
        "score": best_score,
        "source": best_chunk[:200]
    })


if __name__ == "__main__":
    app.run(debug=True)
