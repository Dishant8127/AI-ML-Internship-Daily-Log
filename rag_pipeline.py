import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from langfuse import Langfuse

from datasets import Dataset

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

# =====================================================
# ENV
# =====================================================

load_dotenv()


# RAGAS internally OPENAI_API_KEY શોધે છે
os.environ["OPENAI_API_KEY"] = os.getenv("NVIDIA_API_KEY", "")

# =====================================================
# Langfuse
# =====================================================

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)

# =====================================================
# NVIDIA API Client
# =====================================================

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
)

# =====================================================
# RAGAS NVIDIA LLM
# =====================================================

# ragas_llm = LangchainLLMWrapper(
#     ChatOpenAI(
#         api_key=os.getenv("NVIDIA_API_KEY"),
#         base_url="https://integrate.api.nvidia.com/v1",
#         model="meta/llama-3.1-70b-instruct",
#         temperature=0,
#     )
# )


ragas_llm = LangchainLLMWrapper(
    ChatOpenAI(
        api_key=os.getenv("NVIDIA_API_KEY"),
        base_url="https://integrate.api.nvidia.com/v1",
        model="meta/llama-3.1-70b-instruct",
        temperature=0,
    )
)



# =====================================================
# Sample Documents
# =====================================================

docs = [
    Document(
        page_content="""
        Langfuse is an open-source observability platform
        used for monitoring, tracing and evaluating LLM applications.
        """
    ),
    Document(
        page_content="""
        RAGAS is a framework used to evaluate
        Retrieval Augmented Generation systems.
        """
    ),
]

# =====================================================
# Embeddings
# =====================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =====================================================
# Vector Store
# =====================================================

vectorstore = FAISS.from_documents(
    docs,
    embeddings,
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 2}
)

# =====================================================
# User Question
# =====================================================

question = "What is Langfuse?"

# =====================================================
# Retrieval
# =====================================================

retrieved_docs = retriever.invoke(question)

contexts = [doc.page_content for doc in retrieved_docs]

context_text = "\n".join(contexts)

# =====================================================
# Prompt
# =====================================================

prompt = f"""
Answer only from the provided context.

Context:
{context_text}

Question:
{question}
"""

# =====================================================
# LLM Call
# =====================================================

start_time = time.time()

response = client.chat.completions.create(
    model="meta/llama-3.1-70b-instruct",
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    temperature=0,
)

latency = round(time.time() - start_time, 3)

answer = response.choices[0].message.content

# =====================================================
# Token Usage
# =====================================================

input_tokens = response.usage.prompt_tokens
output_tokens = response.usage.completion_tokens
total_tokens = response.usage.total_tokens

# =====================================================
# Langfuse Logging
# =====================================================

try:
    langfuse.create_event(
        name="rag_pipeline",
        input={
            "question": question,
            "retrieved_context": contexts,
            "prompt": prompt,
        },
        output={
            "answer": answer,
        },
        metadata={
            "latency_seconds": latency,
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": total_tokens,
        },
    )

    langfuse.flush()

except Exception as e:
    print(f"Langfuse Logging Error: {e}")

# =====================================================
# RAGAS Dataset
# =====================================================

evaluation_dataset = Dataset.from_dict(
    {
        "question": [question],
        "answer": [answer],
        "contexts": [contexts],
        "ground_truth": [
            "Langfuse is an open-source observability platform used for monitoring, tracing and evaluating LLM applications."
        ],
    }
)

# =====================================================
# RAGAS Evaluation
# =====================================================

try:
    result = evaluate(
        evaluation_dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
        llm=ragas_llm,
    )

except Exception as e:
    result = f"RAGAS Error: {e}"

# =====================================================
# Output
# =====================================================

print("\n" + "=" * 60)
print("QUESTION")
print("=" * 60)
print(question)

print("\n" + "=" * 60)
print("RETRIEVED CONTEXT")
print("=" * 60)
print(context_text)

print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)
print(answer)

print("\n" + "=" * 60)
print("LATENCY")
print("=" * 60)
print(f"{latency} sec")

print("\n" + "=" * 60)
print("TOKEN USAGE")
print("=" * 60)
print(f"Prompt Tokens     : {input_tokens}")
print(f"Completion Tokens : {output_tokens}")
print(f"Total Tokens      : {total_tokens}")

print("\n" + "=" * 60)
print("RAGAS RESULTS")
print("=" * 60)
print(result)