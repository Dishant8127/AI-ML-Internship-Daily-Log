from models import llm
from models import get_retriever


def ask_contract_question(question):

    retriever = get_retriever()

    if retriever is None:
        return {
            "success": False,
            "answer": "No contract has been uploaded yet.",
            "context": "",
            "prompt": ""
        }

    try:

        docs = retriever.invoke(question)

        if not docs:
            return {
                "success": False,
                "answer": "No relevant contract clauses found.",
                "context": "",
                "prompt": ""
            }

        context = "\n\n".join(
            [
                f"Clause {i+1}:\n{doc.page_content}"
                for i, doc in enumerate(docs)
            ]
        )


        prompt = f"""
You are an expert Legal Contract Assistant.

Your task is to answer ONLY using the contract clauses provided below.

STRICT RULES:

1. Use ONLY the provided contract clauses.
2. Do NOT use outside knowledge.
3. Do NOT make assumptions.
4. Do NOT hallucinate.
5. If the answer is not present in the clauses, respond exactly:

"Information not found in the contract."

6. Mention relevant clause information whenever possible.

CONTRACT CLAUSES:

{context}


QUESTION:

{question}


ANSWER:
"""


        response = llm.invoke(prompt)

        answer = response.content


        return {
            "success": True,
            "answer": answer,
            "context": context,
            "prompt": prompt
        }

    except Exception as e:

        return {
            "success": False,
            "answer": f"Error: {str(e)}",
            "context": "",
            "prompt": ""
        }


