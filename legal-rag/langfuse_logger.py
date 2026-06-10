import os

from dotenv import load_dotenv
from langfuse import Langfuse

load_dotenv()


langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)


def create_trace( question,context,prompt,answer,latency,token_usage=None):


    try:

        trace = langfuse.trace(
            name="legal-contract-rag",
            input=question,
            output=answer
        )


        trace.span(
            name="retrieval",
            input=question,
            output=context,
            metadata={
                "retrieved_context": context
            }
        )

        trace.span(
            name="prompt",
            metadata={
                "prompt": prompt
            }
        )


        trace.span(
            name="generation",
            input=prompt,
            output=answer,
            metadata={
                "latency_seconds": round(latency, 2)
            }
        )

        if token_usage:

            trace.event(
                name="token_usage",
                metadata=token_usage
            )

        langfuse.flush()

        return trace

    except Exception as e:

        print("Langfuse Trace Error:", e)

        return None

def log_ragas_scores(trace, scores):

    try:

        if trace is None:
            return

        trace.event(
            name="ragas_evaluation",
            metadata={
                "faithfulness": scores.get(
                    "faithfulness"
                ),

                "answer_relevancy": scores.get(
                    "answer_relevancy"
                ),

                "context_precision": scores.get(
                    "context_precision"
                ),

                "context_recall": scores.get(
                    "context_recall"
                )
            }
        )

        langfuse.flush()

    except Exception as e:

        print(
            "RAGAS Logging Error:",
            e
        )