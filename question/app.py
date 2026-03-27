from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from utils import chunk_text, extract_text, retrieve_top_k
from models import get_embedding, generate_answer
from vector_store import add_to_store, get_store

load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = "data/docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 🔹 Upload Files
@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")

    for file in files:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        text = extract_text(path)
        chunks = chunk_text(text)

        for chunk in chunks:
            embedding = get_embedding(chunk)
            add_to_store(chunk, embedding)

    return jsonify({"message": "Files processed successfully"})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")

    store = get_store()

    if not store:
        return jsonify({"answer": "No documents uploaded yet."})

    top_chunks = retrieve_top_k(question, store, k=3)

    print("\n===== Top 3 Retrieved Chunks =====")
    for i, (score, chunk) in enumerate(top_chunks, 1):
        print(f"\nRank {i}")
        print(f"Score: {score}")
        print(f"Chunk: {chunk[:200]}")


    context = "\n\n".join([chunk for _, chunk in top_chunks])
    best_score = top_chunks[0][0]
    answer = generate_answer(question, context)

    return jsonify({
        # "question": question,
        "answer": answer,
        "score" : best_score
    })



if __name__ == "__main__":
    app.run(debug=True)