from flask import Flask, request, jsonify
import os

from search import search_similar_image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"


@app.route('/')
def home():
    return "Image Similarity Search API Running!"


@app.route('/search', methods=['POST'])
def search():

    if 'image' not in request.files:
        return jsonify({
            "error": "No image uploaded"
        }), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({
            "error": "No selected file"
        }), 400

    image_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    file.save(image_path)

    results = search_similar_image(image_path)

    return jsonify({
        "matches": results
    })


if __name__ == '__main__':
    app.run(debug=True)