from transformers import pipeline

qa_pipeline = pipeline("question-answering")

def get_answer(context, question):
    result = qa_pipeline(question=question, context=context)

    return {
        "answer": result["answer"],
        "confidence_score": float(result["score"])
    }