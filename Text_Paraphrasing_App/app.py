from flask import Flask, request, jsonify
from models import paraphrase_text

app = Flask(__name__)

@app.route("/paraphrase", methods=["POST"])
def paraphrase():
    data = request.get_json()

    text = data.get("text")
    tone = data.get("tone", "neutral")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    try:
        output = paraphrase_text(text, tone)

        return jsonify({
            "original_text": text,
            "tone": tone,
            "paraphrased_text": output
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)