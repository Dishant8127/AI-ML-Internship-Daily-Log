from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

employees = {
    "Ravi": "Ravi - Software Developer - Salary: 50000 INR",
    "Amit": "Amit - Data Analyst - Salary: 45000 INR",
    "Neha": "Neha - UI Designer - Salary: 40000 INR"
}

def get_employee(name: str):
    return employees.get(name, "Employee not found")

tools = [get_employee]

user_input = "Show details of employee Ravi"
# user_input = input("Enter query: ")

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

    result = get_employee(fc.args["name"])

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