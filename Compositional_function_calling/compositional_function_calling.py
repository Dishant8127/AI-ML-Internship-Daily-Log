import json
from google import genai
from google.genai import types

from dotenv import load_dotenv
import os

load_dotenv() 

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_weather(city: str):
    weather = {
        "Tokyo": {
            "temperature": 18,
            "condition": "Rainy",
            "humidity": 72
        },
        "Paris": {
            "temperature": 24,
            "condition": "Sunny",
            "humidity": 40
        }
    }

    return weather.get(city, {
        "temperature": "unknown",
        "condition": "unknown"
    })


def suggest_clothing(condition: str, temperature: int):

    suggestions = []

    if temperature < 10:
        suggestions.append("heavy jacket")

    elif temperature < 20:
        suggestions.append("light jacket")

    else:
        suggestions.append("t-shirt")

    if condition.lower() == "rainy":
        suggestions.append("umbrella")

    return {
        "recommended_items": suggestions
    }

tools = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_weather",
                description="Get current weather for  city",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "city": {
                            "type": "STRING",
                            "description": "City name"
                        }
                    },
                    "required": ["city"]
                }
            ),
            types.FunctionDeclaration(
                name="suggest_clothing",
                description="Suggest clothing based on weather",
                parameters={
                    "type": "OBJECT",
                    "properties": {
                        "condition": {
                            "type": "STRING"
                        },
                        "temperature": {
                            "type": "INTEGER"
                        }
                    },
                    "required": [
                        "condition",
                        "temperature"
                    ]
                }
            )
        ]
    )
]

available_functions = {
    "get_weather": get_weather,
    "suggest_clothing": suggest_clothing
}

user_input = """ Find the weather in Tokyo and suggest what clothes I should pack. """

contents = [
    types.Content(
        role="user",
        parts=[types.Part(text=user_input)]
    )
]


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
        print("\nFINAL ANSWER:\n")
        print(response.text)
        break


    for fc in function_calls:

        function_name = fc.name
        args = dict(fc.args)

        print(f"\nCalling Function: {function_name}")
        print(f"Arguments: {args}")

        result = available_functions[function_name](**args)

        print(f"Function Result: {result}")

        function_response_part = types.Part.from_function_response(
            name=function_name,
            response={
                "result": result
            }
        )

        contents.append(
            types.Content(
                role="tool",
                parts=[function_response_part]
            )
        )