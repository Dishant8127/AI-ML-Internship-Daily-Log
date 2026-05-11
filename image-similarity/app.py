from flask import Flask,request,jsonify

from PIL import Image

from model import generate_embedding
from search import search_similar

app = Flask(__name__)

@app.route("/search", methods=["POST"])
def search():

    if "image" not in request.files:

        return jsonify({
            "error": "No image uploaded"
        }), 400

    file = request.files["image"]

    try:

        image = Image.open(file.stream ).convert("RGB")

    except Exception as e:

        return jsonify({
            "error": "Invalid image file",
            "details": str(e)
        }), 400

    query_embedding = generate_embedding(image)

    results = search_similar(query_embedding)

    return jsonify(results)

if __name__ == "__main__":

    app.run(debug=True)