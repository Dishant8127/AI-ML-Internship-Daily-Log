from flask import Flask, request, jsonify
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

model = SentenceTransformer("all-MiniLM-L6-v2")


@app.route("/")
def home():
    return jsonify({
        "message": "Pinecone RAG API Running"
    })


@app.route("/search", methods=["POST"])
def search():

    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({
            "error": "query field is required"
        }), 400

    query = data["query"]

    query_embedding = model.encode(query).tolist()

    results = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True
    )

    answer = "No relevant information found."

    for match in results["matches"]:
        if match["score"] > 0.50:
            answer = match["metadata"]["text"]
            break

    return jsonify({
        "query": query,
        "answer": answer
    })


if __name__ == "__main__":
    app.run(debug=True)