# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)

# Load the dataset
data = pd.read_csv("your_dataset.csv")

# Convert 'Expiration Date' to datetime
data["Expiration Date"] = pd.to_datetime(data["Expiration Date"])


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


@app.route("/predict", methods=["POST"])
def predict():
    content = request.json
    product_name = content.get("product_name")
    demand = content.get("demand")
    season = content.get("season")
    trained_model_for_product = train_model_for_product(product_name)

    if trained_model_for_product:
        predicted_price = predict_price(trained_model_for_product, demand, season)
        return jsonify({"predicted_price": predicted_price}), 200
    else:
        return jsonify({"error": "Model not trained for product " + product_name}), 400


if __name__ == "__main__":
    app.run(debug=True)
