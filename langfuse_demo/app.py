from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.langchain import CallbackHandler

load_dotenv()

langfuse_handler = CallbackHandler()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.5
)

while True:

    question = input("\nAsk Question: ")

    if question.lower() == "exit":
        break

    response = llm.invoke(
        question,
        config={
            "callbacks": [langfuse_handler]
        }
    )

    print("\nAnswer:")
    print(response.content)