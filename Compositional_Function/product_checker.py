from google import genai
from google.genai import types

from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def check_product_stock(product_name: str):

    stock_data = {
        "iphone 15": True,
        "macbook air m2": True,
        "playstation 5": False,
        "samsung s24 ultra": True,
        "airpods pro": True,
        "asus rog strix": False,
        "lenovo legion 5": True,
        "ipad air": True,
        "sony wh-1000xm5": False,
        "apple watch series 9": True,
        "nothing phone 2": True,
        "oneplus 12": True,
        "nintendo switch": False,
        "hp pavilion 15": True,
        "dell xps 13": True
    }

    in_stock = stock_data.get(product_name.lower(),False )

    return {
        "product": product_name,
        "in_stock": in_stock
    }

def get_product_price(product_name: str):

    prices = {
        "iphone 15": "79999 INR",
        "macbook air m2": "99999 INR",
        "playstation 5": "54999 INR",
        "samsung s24 ultra": "124999 INR",
        "airpods pro": "24999 INR",
        "asus rog strix": "145000 INR",
        "lenovo legion 5": "89999 INR",
        "ipad air": "59999 INR",
        "sony wh-1000xm5": "29999 INR",
        "apple watch series 9": "41999 INR",
        "nothing phone 2": "37999 INR",
        "oneplus 12": "64999 INR",
        "nintendo switch": "32999 INR",
        "hp pavilion 15": "68999 INR",
        "dell xps 13": "129999 INR"
    }

    return {
        "product": product_name,
        "price": prices.get(product_name.lower(),"Price not available" )
    }


tools = [
    types.Tool(
        function_declarations=[

            types.FunctionDeclaration(
                name="check_product_stock",
                description="Check if product is available in stock",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "product_name": {
                            "type": "STRING",
                            "description": "Name of the product"
                        }
                    },
                    "required": ["product_name"]
                }
            ),

            types.FunctionDeclaration(
                name="get_product_price",
                description="Get product price",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "product_name": {
                            "type": "STRING",
                            "description": "Name of the product"
                        }
                    },
                    "required": ["product_name"]
                }
            )
        ]
    )
]


available_functions = {
    "check_product_stock": check_product_stock,
    "get_product_price": get_product_price
}


user_input = """ Check availability and price for playstation 5 """


contents = [types.Content(role="user",parts=[types.Part(text=user_input)])]


while True:

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            tools=tools,
            temperature=0.3
        )
    )

    candidate = response.candidates[0]

    content = candidate.content

    contents.append(content)

    function_calls = []

    for part in content.parts:

        if part.function_call:

            function_calls.append(part.function_call)

    if not function_calls:

        print("\nSummary:\n")

        print(response.text)

        break

    for fc in function_calls:

        function_name = fc.name

        args = dict(fc.args)

        print(f"\nCalling Function: {function_name}")

        print(f"Arguments: {args}")

        result = available_functions[function_name](**args)

        print(f"Function Result: {result}")

        function_response_part = (
            types.Part.from_function_response(
                name=function_name,
                response={"result": result}
            )
        )

        contents.append(
            types.Content(
                role="tool",
                parts=[function_response_part]
            )
        )