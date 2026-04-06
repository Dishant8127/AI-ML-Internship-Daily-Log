from flask import Flask , request ,jsonify
from logger import log_request
from models import call_nvidia_api

app = Flask(__name__)

@app.route("/generate-text", methods=["POST"])
def generate_text():
    data = request.get_json()

    if not data or "prompt" not in data:
        return jsonify({
            "status": "error",
            "message": "Input text is required."
        }), 400

    prompt = data["prompt"]

    log_request("/generate-text", prompt)

    result = call_nvidia_api(prompt, task="generate")

    return jsonify({
        "data": result
    })


@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({
            "status": "error",
            "message": "Input text is required."
        }), 400

    text = data["text"]

    log_request("/summarize", text)

    result = call_nvidia_api(text, task="summarize")

    return jsonify({
        "data": result
    })




@app.route("/analyze-prompt", methods=["POST"])
def analyze_prompt():
    data = request.get_json()

    if not data or "prompt" not in data:
        return jsonify({
            "status": "error",
            "message": "Input text is required."
        }), 400

    prompt = data["prompt"]

    log_request("/analyze-prompt", prompt)

    keywords = prompt.split()
    intent = "general"

    if "buy" in prompt.lower():
        intent = "purchase"
    elif "learn" in prompt.lower():
        intent = "education"

    return jsonify({
        "keywords": keywords,
        "intent": intent
    })


if __name__ == "__main__":
    app.run(debug=True)