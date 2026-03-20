from flask import Flask
from routes import upload_docs, ask_docs
import os

app = Flask(__name__)

os.makedirs("data", exist_ok=True)
os.makedirs("data/docs", exist_ok=True)


app.add_url_rule("/upload_docs", "upload_docs", upload_docs, methods=["POST"])
app.add_url_rule("/ask_docs", "ask_docs", ask_docs, methods=["POST"])


if __name__ == "__main__":
    app.run(debug=True)