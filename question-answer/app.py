from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from utils import add_document, search  , score_answer #, select_top_chunks , rerank_results
from models import generate_answer

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "docs")

app = Flask(__name__)
os.makedirs("data/docs", exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    files = request.files.getlist("files")
    if not files:
        return {"error": "No files uploaded"}, 400
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        add_document(file_path)
    return {"message": "Files uploaded and processed successfully"}, 200



@app.route("/question", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return {"error": "No question provided"}, 400
    results = search(question, top_k=3)

    if not results:
        return {"error": "No relevant documents found"}, 404

    # context_chunks = []
    # for score, item in results:
    #     context_chunks.append(item["text"])
    context_chunks = []

    print("\n=== Retrieved Chunks & Scores ===")

    for i, (score, item) in enumerate(results):
        print(f"\nChunk {i+1}")
        print(f"Score: {score:.4f}")
        print(f"Text: {item['text'][:200]}...")  # limit text

        context_chunks.append(item["text"])
    

    context = " ".join(context_chunks).strip()

    if not context:
        return {"error": "Context is empty"}, 500
    
    answer = generate_answer(question, context)
    confidence = score_answer(answer, context)

    return {"answer": answer,"score": confidence}, 200

if __name__ == "__main__":
    app.run(debug=True)
