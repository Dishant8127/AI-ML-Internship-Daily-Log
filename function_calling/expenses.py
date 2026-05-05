from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

expenses = []

def add_expense(amount: float, category: str):

    expenses.append({"amount": amount, "category": category})

    total = sum(item["amount"] for item in expenses)

    return f"{amount} INR added to {category}. Total expense: {total} INR."

tools = [add_expense]

user_input = "Today I spent 500 on food"
# user_input = input("Enter your expense: ")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_input,
    config={
        "tools": tools
    }
)

part = response.candidates[0].content.parts[0]

if hasattr(part, "function_call") and part.function_call:
    fc = part.function_call

    result = add_expense(fc.args["amount"], fc.args["category"])

    final_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            user_input,
            {
                "function_response": {
                    "name": fc.name,
                    "response": {
                        "result": result
                    }
                }
            }
        ]
    )

    print(final_response.text)

else:
    print(response.text)