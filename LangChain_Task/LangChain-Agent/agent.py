from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, initialize_agent
from langchain.agents import AgentType

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0)

def calculator(query):
    return str(eval(query))

tools = [
    Tool(
        name="Calculator",
        func=calculator,
        description="Useful for mathematical calculations"
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

response = agent.run("What is 25 * 10 + 100 ?")

print("\nAgent Response:")
print(response)