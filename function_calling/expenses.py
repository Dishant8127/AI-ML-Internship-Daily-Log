import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

expenses = []

def add_expense(amount, category):
    expenses.append({"amount": amount, "category": category})
    
    total = sum(item["amount"] for item in expenses)
    
    return f"{amount} INR added to {category}. Total expense: {total} INR."

tools = [
    {
        "function_declarations": [
            {
                "name": "add_expense",
                "description": "Add a daily expense with category",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "Expense amount"
                        },
                        "category": {
                            "type": "string",
                            "description": "Expense category like food, travel, shopping"
                        }
                    },
                    "required": ["amount", "category"]
                }
            }
        ]
    }
]

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=tools
)

user_input = "Today I spent 500 on food"

response = model.generate_content(user_input)

part = response.candidates[0].content.parts[0]

if hasattr(part, "function_call"):
    function_call = part.function_call
    
    function_name = function_call.name
    args = function_call.args

    if function_name == "add_expense":
        result = add_expense(args["amount"], args["category"])

        final_response = model.generate_content([
            user_input,
            {
                "function_response": {
                    "name": function_name,
                    "response": {
                        "result": result
                    }
                }
            }
        ])

        print(final_response.text)

else:
    print(response.text)