from flask import Flask, request, jsonify
from models import embedding_model, llm, index


app = Flask(__name__)



@app.route("/ask", methods=["POST"])
def ask():

    data = request.json
    query = data["question"]

    query_embedding = embedding_model.encode(
        query
    ).tolist()

    result = index.query(
        vector=query_embedding,
        top_k=3,
        include_metadata=True
    )

    context = ""

    for match in result["matches"]:
        context += match["metadata"]["text"] + "\n"

    prompt = f"""
    Context:
    {context}

    Question:
    {query}

    Answer based only on context.
    """

    response = llm.generate_content(prompt)

    return jsonify({
        "question": query,
        "context": context,
        "answer": response.text
    })

if __name__ == "__main__":
    app.run(debug=True)