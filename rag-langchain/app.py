from flask import Flask, request, jsonify

from models import retriever, llm

app = Flask(__name__)


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data["question"]

    docs = retriever.invoke(question)

    context = "\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
    Answer only using the context below.

    Context:
    {context}

    Question:
    {question}
    """

    response = llm.invoke(prompt)

    return jsonify({
        "question": question,
        "context": context,
        "answer": response.content
    })


if __name__ == "__main__":
    app.run(debug=True)