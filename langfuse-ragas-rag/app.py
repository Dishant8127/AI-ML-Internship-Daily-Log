import os
import time
import ast

from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template

from dotenv import load_dotenv

from rag_pipeline import create_vector_store,ask_question

from evaluator import evaluate_rag

from langfuse import Langfuse

load_dotenv()

app = Flask(__name__)

langfuse = Langfuse()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:

        return jsonify(
            {
                "error": "No file uploaded"
            }
        )

    pdf = request.files["file"]


    path = os.path.join("uploads",pdf.filename)

    pdf.save(path)

    create_vector_store(path)

    return jsonify(
        {
            "message": "PDF uploaded and indexed successfully"
        }
    )


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data["question"]

    start_time = time.time()

    result = ask_question(question)

    end_time = time.time()

    latency = round( end_time - start_time,2 )

    token_usage = (
        len(result["prompt"].split())
        +
        len(result["answer"].split())
    )

    trace = langfuse.trace(
        name="legal-rag-system"
    )

    trace.event(
        name="user-question",
        input=result["question"]
    )

    trace.event(
        name="retrieved-context",
        input=result["context"]
    )

    trace.event(
        name="prompt",
        input=result["prompt"]
    )

    trace.event(
        name="final-answer",
        output=result["answer"]
    )

    trace.score(
        name="latency",
        value=latency
    )

    trace.score(
        name="token-usage",
        value=token_usage
    )

    ragas_result = evaluate_rag(
        result["question"],
        result["answer"],
        result["context"]
    )

    return jsonify(
        {
            "answer": result["answer"],
            "latency_seconds": latency,
            "token_usage": token_usage,
            "ragas_metrics": ast.literal_eval(str(ragas_result).replace("nan", "None"))
        }
    )


if __name__ == "__main__":

    app.run(debug=True)
