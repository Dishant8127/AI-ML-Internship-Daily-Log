from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

texts = [
    "LangChain is a framework for LLM applications.",
    "It provides prompt templates and chains.",
    "It supports vector databases and RAG.",
    "It also supports AI Agents."
]

docs = [Document(page_content=t) for t in texts]

chain = load_summarize_chain(
    llm,
    chain_type="refine"
)

result = chain.invoke(docs)

print("\nRefine Summary:")
print(result["output_text"])