import os
from flask import request, jsonify
from model import qa_pipeline
from utils import add_document, search

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "docs")


def upload_docs():

    os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    for file in files:

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        add_document(path)

    return jsonify({"message": "Documents uploaded & processed"})


def ask_docs():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    results = search(question, top_k=3)

    if not results:
        return jsonify({"answer": "No relevant data found"}), 200

    answers = []

    for score, item in results:
        response = qa_pipeline(
            question=question,
            context=item["text"]
        )

        answers.append({
            "answer": response["answer"],
            "confidence": float(response["score"]),
            "source_doc": item["source"]
        })

    return jsonify({
        "question": question,
        "answers": answers
    })