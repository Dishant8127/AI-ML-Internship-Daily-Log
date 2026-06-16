from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_nvidia_ai_endpoints import ChatNVIDIA,NVIDIAEmbeddings

load_dotenv()

DB_FOLDER = "chroma_db"

embeddings = NVIDIAEmbeddings()

vectorstore = Chroma(
    persist_directory=DB_FOLDER,
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

llm = ChatNVIDIA(
    model="meta/llama-3.3-70b-instruct",
    temperature=0.2
)


def advisor_agent(user_question):

    docs = retriever.invoke(user_question)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
    You are an Agentic Learning Advisor.

    Your task:

    1. Analyze the student's question.
    2. Use the retrieved context.
    3. Identify important topics.
    4. Prioritize what should be studied first.
    5. Decide what can be skipped if time is limited.
    6. Create a study plan.
    7. Explain your reasoning.

    Student Question:
    {user_question}

    Context:
    {context}

    Return:

    1. Important Topics
    2. Priority Order
    3. Topics To Skip (if any)
    4. Study Plan
    5. Reasoning
    """

    response = llm.invoke(prompt)

    return response.content