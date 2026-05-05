from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

orders = []

def order_food(item: str, quantity: int):
    orders.append({"item": item, "quantity": quantity})
    return f"{quantity} {item}(s) ordered successfully!"

tools = [order_food]

user_input = "I want to order 2 burgers"
# user_input = input("Enter your order: ")

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

    result = order_food(fc.args["item"], fc.args["quantity"])

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