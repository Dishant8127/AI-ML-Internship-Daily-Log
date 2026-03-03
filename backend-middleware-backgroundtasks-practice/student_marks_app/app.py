from flask import Flask, request, jsonify
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


DATA_FILE = os.getenv("DATA_FILE")


@app.before_request
def before_request_logging():
    request.start_time = time.time()
    print("------ API LOG ------")
    print("Endpoint:", request.path)
    print("Method:", request.method)


@app.after_request
def after_request_logging(response):
    time_taken = time.time() - request.start_time
    print("Time Taken:", round(time_taken, 4), "seconds")
    print("---------------------")
    return response


def read_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)



@app.route("/")
def home():
    return "Student Marks JSON CRUD App Running..."


@app.route("/students", methods=["GET"])
def get_students():
    data = read_data()
    return jsonify(data)


@app.route("/students", methods=["POST"])
def add_student():

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    new_student = request.get_json()

    required_fields = ["name", "maths", "science", "english"]
    for field in required_fields:
        if field not in new_student:
            return jsonify({"error": f"{field} is required"}), 400

    data = read_data()

    if len(data) == 0:
        new_id = 1
    else:
        new_id = max(student["id"] for student in data) + 1

    new_student["id"] = new_id
    data.append(new_student)

    save_data(data)

    return jsonify({"message": "Student added successfully", "id": new_id}), 201

@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    updated_data = request.get_json()
    data = read_data()

    for student in data:
        if student["id"] == student_id:
            student["name"] = updated_data.get("name", student["name"])
            student["maths"] = updated_data.get("maths", student["maths"])
            student["science"] = updated_data.get("science", student["science"])
            student["english"] = updated_data.get("english", student["english"])

            save_data(data)
            return jsonify({"message": "Student updated successfully"})

    return jsonify({"error": "Student not found"}), 404


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):

    data = read_data()

    for student in data:
        if student["id"] == student_id:
            data.remove(student)
            save_data(data)
            return jsonify({"message": "Student deleted successfully"})

    return jsonify({"error": "Student not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)