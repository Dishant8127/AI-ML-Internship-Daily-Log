import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings

from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)


def create_vector_store(pdf_path):

    loader = PyPDFLoader(pdf_path)

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    vector_db = FAISS.from_documents( chunks,embeddings)

    vector_db.save_local( "data/faiss_index")

    return True


def ask_question(question):

    vector_db = FAISS.load_local(
        "data/faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = vector_db.similarity_search(
        question,
        k=3
    )

    context = "\n".join(
        [doc.page_content for doc in docs]
    )

    prompt = f"""
You are a legal contract assistant.

Answer ONLY from the provided context.

If the answer is not found,
say:
"I could not find the answer in the contract."

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    return {
        "question": question,
        "context": context,
        "prompt": prompt,
        "answer": response.content
    }