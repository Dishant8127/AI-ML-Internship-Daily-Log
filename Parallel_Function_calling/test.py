from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_notes(subject: str):

    notes = {
        "python": "Python notes: Variables, Loops, Functions, OOP",
        "java": "Java notes: Classes, Objects, Inheritance",
        "sql": "SQL notes: Joins, Queries, Normalization"
    }

    return notes.get(subject.lower(), "Notes not found")


def find_internships(domain: str):

    internships = {
        "python": "Python Internship available at TechCorp",
        "web development": "Web Development Internship at CodeHub",
        "data science": "Data Science Internship at AI Labs"
    }

    return internships.get(domain.lower(), "Internship not found")


def get_interview_questions(topic: str):

    questions = {
        "python": "Top Python Interview Questions: List vs Tuple, OOP, Decorators",
        "java": "Top Java Interview Questions: JVM, JDK, Inheritance",
        "sql": "Top SQL Interview Questions: Joins, Primary Key, Indexing"
    }

    return questions.get(topic.lower(), "Questions not found")

tools = [
    get_notes,
    find_internships,
    get_interview_questions
]


user_input = """
Give simple plain text response.
Do not use markdown symbols like * or #.

I need Python notes, Python internship opportunities,
and Python interview questions
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_input,
    config={
        "tools": tools
    }
)

parts = response.candidates[0].content.parts

tool_responses = []

for part in parts:

    if hasattr(part, "function_call") and part.function_call:

        fc = part.function_call

        if fc.name == "get_notes":

            result = get_notes(fc.args["subject"])

        elif fc.name == "find_internships":

            result = find_internships(fc.args["domain"])

        elif fc.name == "get_interview_questions":

            result = get_interview_questions(fc.args["topic"])

        else:

            result = "Function not found"

        tool_responses.append(
            {
                "function_response": {
                    "name": fc.name,
                    "response": {
                        "result": result
                    }
                }
            }
        )


final_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        user_input,
        *tool_responses
    ]
)


print(final_response.text)