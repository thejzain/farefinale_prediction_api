from flask import Flask, request, jsonify
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

# Initialize Firebase Admin SDK with your credentials
cred = credentials.Certificate("admin.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# Function to fetch data from Firebase
def fetch_data_from_firebase(collection_name):
    docs = db.collection(collection_name).stream()
    data = []
    for doc in docs:
        data.append(doc.to_dict())
    return pd.DataFrame(data)


# Load the dataset from Firebase
data = fetch_data_from_firebase("test_ml")

# Convert 'Expiration Date' to datetime (if applicable)
# data["Expiration Date"] = pd.to_datetime(data["Expiration Date"])


# Train model for a specific product
def train_model_for_product(product_name):
    # Filter data for the specified product
    product_data = data[data["Food Type"] == product_name]

    # Check if there are enough samples for training
    if len(product_data) < 2:
        return jsonify(
            {"error": "Insufficient data for training the model for " + product_name}
        ), 400

    # Extract features and target variable
    X = product_data[["Demand", "Season"]]
    y = product_data["Price"]

    # Convert 'Demand' and 'Season' to categorical variables
    X["Demand"] = pd.Categorical(
        X["Demand"], categories=["Low", "Medium", "High"], ordered=True
    )
    X["Season"] = pd.Categorical(
        X["Season"], categories=["Spring", "Summer", "Autumn", "Winter"], ordered=True
    )

    # One-hot encode categorical features
    X = pd.get_dummies(X)

    # Train Random Forest Regressor model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Return the trained model
    return model


# Function to predict price based on user input
def predict_price(trained_model, demand, season):
    # Create DataFrame with user input
    input_data = pd.DataFrame({"Demand": [demand], "Season": [season]})

    # Convert 'Demand' and 'Season' to categorical variables
    input_data["Demand"] = pd.Categorical(
        input_data["Demand"], categories=["Low", "Medium", "High"], ordered=True
    )
    input_data["Season"] = pd.Categorical(
        input_data["Season"],
        categories=["Spring", "Summer", "Autumn", "Winter"],
        ordered=True,
    )

    # One-hot encode categorical features
    input_data = pd.get_dummies(input_data)

    # Predict price
    predicted_price = trained_model.predict(input_data)[0]

    # Adjust predicted price based on demand and season
    demand_multipliers = {"Low": 0.90, "Medium": 0.95, "High": 1.00}
    season_multipliers = {
        "Spring": 0.85,
        "Summer": 0.90,
        "Autumn": 0.95,
        "Winter": 1.00,
    }

    demand_multiplier = demand_multipliers.get(demand, 1.0)
    season_multiplier = season_multipliers.get(season, 1.0)

    adjusted_price = predicted_price * demand_multiplier * season_multiplier
    return adjusted_price


# Function to save predicted price to Firebase
def save_predicted_price_to_firebase(product_name, predicted_price):
    doc_ref = db.collection("predicted_prices").document(product_name)
    doc_ref.set({"predicted_price": predicted_price})


@app.route("/predict", methods=["POST"])
def predict():
    content = request.json
    predictions = []

    for item in content["items"]:
        product_name = item.get("product_name")
        demand = item.get("demand")
        season = item.get("season")
        trained_model_for_product = train_model_for_product(product_name)

        if trained_model_for_product:
            predicted_price = predict_price(trained_model_for_product, demand, season)
            # Save predicted price to Firebase
            save_predicted_price_to_firebase(product_name, predicted_price)
            predictions.append(
                {"product_name": product_name, "predicted_price": predicted_price}
            )
        else:
            predictions.append(
                {"product_name": product_name, "error": "Model not trained for product"}
            )

    return jsonify({"predictions": predictions}), 200


if __name__ == "__main__":
    app.run(debug=True)
