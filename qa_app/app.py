from flask import Flask, request, jsonify
from model import get_answer

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()

    context = data.get("context")
    question = data.get("question")

    if not context or not question:
        return jsonify({"error": "Both context and question are required"}), 400

    result = get_answer(context, question)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)