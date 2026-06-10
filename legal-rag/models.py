import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()


llm = ChatOpenAI(
    model="meta/llama-3.1-70b-instruct",
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1",
    temperature=0.2,
    max_tokens=1024
)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def load_vectorstore():

    if not os.path.exists("vectorstore"):
        return None

    return FAISS.load_local(
        "vectorstore",
        embedding_model,
        allow_dangerous_deserialization=True
    )

def get_retriever():

    vectorstore = load_vectorstore()

    if vectorstore is None:
        return None

    return vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )