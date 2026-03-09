from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# load trained model
model = joblib.load("model.pkl")

@app.route("/")
def home():
    return "House Price Prediction API"

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    area = data["area_sqft"]
    bedrooms = data["bedrooms"]
    bathrooms = data["bathrooms"]
    floors = data["floors"]
    age = data["age_years"]
    distance = data["distance_city_km"]
    parking = data["parking_spaces"]

    input_data = np.array([[area, bedrooms, bathrooms, floors, age, distance, parking]])

    prediction = model.predict(input_data)

    return jsonify({
        "predicted_price": float(prediction[0])
    })

if __name__ == "__main__":
    app.run(debug=True)