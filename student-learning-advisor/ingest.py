import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

load_dotenv()

DATA_FOLDER = "data"
DB_FOLDER = "chroma_db"

all_docs = []

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(DATA_FOLDER, file))
        docs = loader.load()
        all_docs.extend(docs)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(all_docs)

embeddings = NVIDIAEmbeddings()

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=DB_FOLDER
)
