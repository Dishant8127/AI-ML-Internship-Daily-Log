from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from regex import search
from utils import add_document , search
from flask import request
from models import qa_pipeline

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "docs")

app = Flask(__name__)

os.makedirs("data", exist_ok=True)
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
    best_answer = ""
    best_score = 0.0
    for score, item in results:
        full_context = item["text"]
        response = qa_pipeline(question=question, context=full_context)
        if response["score"] > best_score:
            best_score = response["score"]
            best_answer = response["answer"]
    return {
        "answer": best_answer,
        "score": best_score
    }, 200



if __name__ == "__main__":
    app.run(debug=True)