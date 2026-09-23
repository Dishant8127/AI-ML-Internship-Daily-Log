# Image Similarity Search

A simple image similarity search web app that finds visually similar images using precomputed embeddings and an image similarity model.

## Description

This project provides a small Flask web app that lets you upload a query image and find similar images from a dataset using embedding models. Precomputed embeddings and models are included to run the search quickly without training.

## Features

- Upload an image via the web UI and search for visually similar images.
- Uses precomputed image embeddings for fast nearest-neighbor search.
- Includes trained model files so you can run the app locally.

## Repository Structure

- `app.py` - Flask application entrypoint.
- `embedding_model.keras` - Saved embedding model (Keras).
- `image_similarity_model.keras` - Saved similarity model (Keras).
- `image_embeddings.npy` - Precomputed image embeddings (NumPy array).
- `image_paths.npy` - Paths corresponding to the embeddings.
- `templates/` - Flask HTML templates (`index.html`, `result.html`).
- `static/` - Static assets (CSS and uploaded images).
- `requirements.txt` - Python dependencies.

## Requirements

- Python 3.8 or newer
- pip

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

It is recommended to use a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate    # Windows
python -m pip install -r requirements.txt
```

## Running the app

Start the Flask app:

```bash
python app.py
```

Open your browser and go to `http://127.0.0.1:5000` (or the address shown in the console). Use the web UI to upload a query image and view the most similar images from the dataset.

## Notes

- The project already includes model and data files (`*.keras`, `*.npy`). If you replace or retrain models you may need to recompute `image_embeddings.npy`.
- If you see errors loading models, ensure your installed TensorFlow/Keras version is compatible with the saved models.

## Extending the project

- Add an index-building script to regenerate `image_embeddings.npy` from your dataset.
- Replace the nearest-neighbors search with FAISS for faster, scalable search.
- Add pagination or result scoring display in the UI.

## License

This repository does not include an explicit license. Add one if you plan to share or publish the code.

## Contact

If you want changes to this README or help running the app, tell me what you'd like improved.
