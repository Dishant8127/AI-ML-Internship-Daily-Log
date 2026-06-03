from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

load_dotenv()

llm = ChatGoogleGenerativeAI( model="gemini-2.5-flash",temperature=0.3)

text = """
LangChain is a framework used for developing applications powered by Large Language Models.
It helps developers build chatbots, AI assistants, RAG systems, agents and many other AI applications.
LangChain provides integrations with various LLMs, vector databases and tools.
"""

docs = [Document(page_content=text)]

chain = load_summarize_chain(
    llm,
    chain_type="stuff"
)

result = chain.invoke(docs)

print("\nSummary:")
print(result["output_text"])