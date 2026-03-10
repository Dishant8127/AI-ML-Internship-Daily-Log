from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

model = joblib.load("model.pkl")

@app.route("/")
def home():
    return "Random Forest Iris Prediction API"

@app.route("/predict", methods=["POST"])
def predict():

    data = request.json

    sepal_length = data["sepal_length"]
    sepal_width = data["sepal_width"]
    petal_length = data["petal_length"]
    petal_width = data["petal_width"]

    features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])

    prediction = model.predict(features)

    return jsonify({
        "prediction": prediction[0]
    })

if __name__ == "__main__":
    app.run(debug=True)