from flask import Flask
from routes import upload_docs, start_session, ask_session, clear_session, get_sessions, get_history, delete_session
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

os.makedirs("data", exist_ok=True)
os.makedirs("data/docs", exist_ok=True)

app.add_url_rule("/upload_docs", "upload_docs", upload_docs, methods=["POST"])
app.add_url_rule("/start_session", "start_session", start_session, methods=["GET"])
app.add_url_rule("/ask_session", "ask_session", ask_session, methods=["POST"])
app.add_url_rule("/clear_session", "clear_session", clear_session, methods=["POST"])
app.add_url_rule("/get_sessions", "get_sessions", get_sessions, methods=["GET"])
app.add_url_rule("/get_history", "get_history", get_history, methods=["POST"])
app.add_url_rule("/delete_session", "delete_session", delete_session, methods=["POST"])

if __name__ == "__main__":
    app.run(debug=True)