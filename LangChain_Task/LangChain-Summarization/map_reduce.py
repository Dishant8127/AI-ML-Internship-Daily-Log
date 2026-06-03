from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

text = """
LangChain is an open-source framework.
It supports prompt engineering.
It supports retrieval augmented generation.
It provides integrations with vector databases.
It helps in building AI Agents.
It can work with Gemini, OpenAI and many other models.
"""

docs = [Document(page_content=text)]

chain = load_summarize_chain(
    llm,
    chain_type="map_reduce"
)

result = chain.invoke(docs)

print("\nMap Reduce Summary:")
print(result["output_text"])