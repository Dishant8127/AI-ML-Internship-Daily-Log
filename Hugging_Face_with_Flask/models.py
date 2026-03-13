from flask import request, jsonify
from transformers import pipeline

summarizer = pipeline("summarization")

def summarize_text():
    data = request.json
    text = data.get("text")

    result = summarizer(text, max_length=60, min_length=20)

    return jsonify({
        "summary": result[0]["summary_text"]
    })


ner_model = pipeline("ner")

def ner_text():
    data = request.json
    text = data.get("text")

    entities = ner_model(text)

    for entity in entities:
        entity["score"] = float(entity["score"])

    return jsonify({
        "entities": entities
    })