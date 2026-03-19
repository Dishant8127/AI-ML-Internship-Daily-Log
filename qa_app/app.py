from flask import Flask, request, jsonify
import os
from model import qa_pipeline
from utils import extract_text, split_text

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")
    context = data.get("context")

    result = qa_pipeline(question=question, context=context)

    return jsonify({
        "answer": result["answer"],
        "start": result["start"],
        "end": result["end"],
        "confidence": float(result["score"])
    })


@app.route("/ask_file", methods=["POST"])
def ask_file():
    file = request.files["file"]
    question = request.form.get("question")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    text = extract_text(file_path)

    chunks = split_text(text)

    best_answer = None
    best_score = 0

    for chunk in chunks:
        result = qa_pipeline(question=question, context=chunk)

        if result["score"] > best_score:
            best_score = result["score"]
            best_answer = result

    return jsonify({
        "answer": best_answer["answer"],
        "start": best_answer["start"],
        "end": best_answer["end"],
        "confidence": float(best_score)
    })



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)