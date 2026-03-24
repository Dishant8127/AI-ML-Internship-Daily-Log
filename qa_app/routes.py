import os
import uuid
import json
from flask import request, jsonify
from model import qa_pipeline
from utils import add_document, search

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "docs")
SESSION_FILE = os.path.join(BASE_DIR, "sessions.json")


def load_sessions():
    if not os.path.exists(SESSION_FILE):
        return {}
    with open(SESSION_FILE, "r") as f:
        return json.load(f)


def save_sessions(data):
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)


sessions = load_sessions()


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


def start_session():
    global sessions
    session_id = str(uuid.uuid4())
    sessions[session_id] = []
    save_sessions(sessions)
    return jsonify({"session_id": session_id})


def ask_session():
    global sessions

    data = request.get_json()
    session_id = data.get("session_id")
    question = data.get("question")

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session_id"}), 400

    if not question:
        return jsonify({"error": "Question is required"}), 400

    history = sessions[session_id]

    history_context = " ".join([
        f"Q: {item['q']} A: {item['a']}"
        for item in history
    ])

    results = search(question, top_k=3)

    if not results:
        return jsonify({
            "answer": "No relevant data found",
            "history": history
        }), 200

    best_answer = ""
    best_score = 0.0
    best_source = ""

    for score, item in results:
        full_context = history_context + " " + item["text"]

        response = qa_pipeline(
            question=question,
            context=full_context
        )

        if response["score"] > best_score:
            best_score = float(response["score"])
            best_answer = response["answer"]
            best_source = item["source"]

    history.append({
        "q": question,
        "a": best_answer
    })

    if len(history) > 5:
        history.pop(0)

    sessions[session_id] = history
    save_sessions(sessions)

    return jsonify({
        "answer": best_answer,
        "source": best_source,
        "confidence": best_score,
        "history": history
    })


def clear_session():
    global sessions

    data = request.get_json()
    session_id = data.get("session_id")

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session_id"}), 400

    sessions[session_id] = []
    save_sessions(sessions)

    return jsonify({"message": "Session history cleared"})

def delete_session():
    global sessions

    data = request.get_json()
    session_id = data.get("session_id")

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session_id"}), 400

    del sessions[session_id]
    save_sessions(sessions)

    return jsonify({"message": "Session deleted"})

def get_sessions():
    return jsonify({
        "sessions": list(sessions.keys())
    })


def get_history():
    data = request.get_json()
    session_id = data.get("session_id")

    if not session_id or session_id not in sessions:
        return jsonify({"error": "Invalid session_id"}), 400

    return jsonify({
        "history": sessions[session_id]
    })