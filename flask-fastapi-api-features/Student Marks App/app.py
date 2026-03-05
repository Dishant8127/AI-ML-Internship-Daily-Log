from flask import Flask, request, jsonify
from helper import validate_marks, calculate_average

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Resource Not Found",
        "status": 404
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad Request",
        "status": 400
    }), 400


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal Server Error",
        "status": 500
    }), 500



@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "UP",
        "framework": "Flask",
        "version": "v1"
    })


@app.route("/calculateAverage", methods=["POST"])
def calculate_average_api():

    data = request.get_json()

    if not data or "marks" not in data:
        return jsonify({
            "error": "Marks field is required"
        }), 400

    marks = data["marks"]

    valid, message = validate_marks(marks)

    if not valid:
        return jsonify({
            "error": message
        }), 400

    avg = calculate_average(marks)

    return jsonify({
        "marks": marks,
        "average": avg
    })


if __name__ == "__main__":
    app.run(debug=True)