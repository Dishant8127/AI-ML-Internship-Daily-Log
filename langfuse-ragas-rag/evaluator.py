from datasets import Dataset

from ragas import evaluate

from ragas.metrics import faithfulness,answer_relevancy,context_precision,context_recall

from rag_pipeline import llm, embeddings

def evaluate_rag(question, answer, context):

    dataset = Dataset.from_dict(
        {
            "question": [question],
            "answer": [answer],
            "contexts": [[context]],
            "ground_truth": [answer]
        }
    )

    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ],
        llm=llm,
        embeddings=embeddings
    )

    return result