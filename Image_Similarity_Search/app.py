import os
import numpy as np
import tensorflow as tf

from flask import Flask, render_template, request
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

IMG_SIZE = 224

print("Loading Embedding Model...")

embedding_model = tf.keras.models.load_model(
    "embedding_model.keras",
    compile=False
)


image_embeddings = np.load("image_embeddings.npy")
image_paths = np.load(
    "image_paths.npy",
    allow_pickle=True
)

print(f"Total Images : {len(image_paths)}")

def generate_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((IMG_SIZE, IMG_SIZE))
    image = np.array(image).astype("float32")
    image = preprocess_input(image)
    image = np.expand_dims(image, axis=0)
    embedding = embedding_model.predict(
        image,
        verbose=0
    )
    return embedding

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():

    if "image" not in request.files:
        return "No image uploaded."

    file = request.files["image"]

    if file.filename == "":
        return "Please select an image."

    upload_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(upload_path)
    query_embedding = generate_embedding(upload_path)
    similarity = cosine_similarity(
        query_embedding,
        image_embeddings
    )

    similarity = similarity.flatten()
    top_indices = np.argsort(similarity)[::-1][:20]
    results = []
    count = 0

    for index in top_indices:
        image_path = image_paths[index]
        if os.path.exists(image_path):
            results.append({
                "image": image_path.replace("\\", "/"),
                "score": round(
                    float(similarity[index] * 100),
                    2
                )
            })
            count += 1
        if count == 5:
            break

    return render_template(
        "result.html",
        query_image=upload_path.replace("\\", "/"),
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)