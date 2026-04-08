from flask import Flask, request, jsonify
from model import generate_text, summarize_text

app = Flask(__name__)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    result = generate_text(prompt)
    return jsonify({"response": result})


@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    text = data.get("text")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    result = summarize_text(text)
    return jsonify({"summary": result})


if __name__ == "__main__":
    app.run(debug=True)