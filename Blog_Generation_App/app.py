from flask import Flask, request, jsonify
from model import generate_text

app = Flask(__name__)
@app.route("/generate_article", methods=["POST"])
def generate_article():
    data = request.get_json()
    topic = data.get("topic")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    try:
        output = generate_text(topic)
        return jsonify({
            "article": output
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
    

if __name__ == "__main__":
    app.run(debug=True)

