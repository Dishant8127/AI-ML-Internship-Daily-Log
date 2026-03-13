from flask import Flask
import models

app = Flask(__name__)

@app.route("/")
def home():
    return "Hugging Face Flask API"

@app.route("/summarize", methods=["POST"])
def summarize():
    return models.summarize_text()

@app.route("/ner", methods=["POST"])
def ner():
    return models.ner_text()

if __name__ == "__main__":
    app.run(debug=True)