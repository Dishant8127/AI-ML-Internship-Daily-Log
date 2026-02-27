from flask import Flask, request, jsonify
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get base directory (Flask folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Option 1: Use .env path if provided
env_path = os.getenv("DATA_FILE")

if env_path:
    DATA_FILE = os.path.join(BASE_DIR, os.path.basename(env_path))
else:
    # Default fallback
    DATA_FILE = os.path.join(BASE_DIR, "data.json")

print("Using DATA_FILE:", DATA_FILE)


# --------------------------
# Utility Functions
# --------------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


# --------------------------
# Routes
# --------------------------

@app.route("/")
def home():
    return jsonify({"message": "API is working"})


@app.route("/students", methods=["GET"])
def get_students():
    data = load_data()
    return jsonify(data)


@app.route("/students/<student_id>", methods=["GET"])
def get_student(student_id):
    data = load_data()

    if student_id in data:
        return jsonify(data[student_id])

    return jsonify({"error": "Student not found"}), 404


@app.route("/students", methods=["POST"])
def add_student():
    data = load_data()
    new_data = request.json

    if not new_data or "name" not in new_data or "age" not in new_data:
        return jsonify({"error": "Name and age are required"}), 400

    new_id = str(int(max(data.keys(), default="0")) + 1)

    data[new_id] = {
        "name": new_data["name"],
        "age": new_data["age"]
    }

    save_data(data)

    return jsonify({
        "message": "Student added",
        "student_id": new_id,
        "student": data[new_id]
    }), 201


@app.route("/students/<student_id>", methods=["PUT"])
def update_student(student_id):
    data = load_data()

    if student_id not in data:
        return jsonify({"error": "Student not found"}), 404

    new_data = request.json

    if not new_data or "name" not in new_data or "age" not in new_data:
        return jsonify({"error": "Name and age are required"}), 400

    data[student_id]["name"] = new_data["name"]
    data[student_id]["age"] = new_data["age"]

    save_data(data)

    return jsonify({
        "message": "Student updated",
        "student": data[student_id]
    })


@app.route("/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    data = load_data()

    if student_id not in data:
        return jsonify({"error": "Student not found"}), 404

    deleted_student = data.pop(student_id)
    save_data(data)

    return jsonify({
        "message": "Student deleted",
        "student": deleted_student
    })


# --------------------------
# Run App
# --------------------------

if __name__ == "__main__":
    app.run(debug=True)