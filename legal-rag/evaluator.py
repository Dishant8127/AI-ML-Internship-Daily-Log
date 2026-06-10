from datasets import Dataset

from ragas import evaluate

from ragas.metrics import faithfulness,answer_relevancy,context_precision,context_recall


def evaluate_rag_response(question,answer, context):


    try:

        contexts = [[context]]

        dataset = Dataset.from_dict(
            {
                "question": [question],
                "answer": [answer],
                "contexts": contexts
            }
        )

        result = evaluate(
            dataset=dataset,
            metrics=[
                faithfulness,
                answer_relevancy
            ]
        )

        scores = result.to_pandas().iloc[0].to_dict()

        return {
            "faithfulness": round(
                scores.get("faithfulness", 0),
                4
            ),

            "answer_relevancy": round(
                scores.get("answer_relevancy", 0),
                4
            ),

            "context_precision": round(
                scores.get("context_precision", 0),
                4
            ),

            "context_recall": round(
                scores.get("context_recall", 0),
                4
            )
        }

    except Exception as e:

        import traceback

        traceback.print_exc()

        return {
            "faithfulness": 0,
            "answer_relevancy": 0,
            "context_precision": 0,
            "context_recall": 0
        }