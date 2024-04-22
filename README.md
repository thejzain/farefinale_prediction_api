

## Food Price Prediction API

This Flask API predicts the price of a food item based on its demand and season.

### Dependencies

* Flask
* pandas
* scikit-learn

### Usage

1. **Create a CSV dataset:** 
    - The dataset should have columns for "Food Type" (product name), "Demand" (Low, Medium, High), "Season" (Spring, Summer, Autumn, Winter), "Expiration Date", and "Price".
    - Replace "your_dataset.csv" in the code with the actual filename of your dataset.

2. **Run the API:**
    - Save the code as `food_price_prediction.py`.
    - Open a terminal and navigate to the directory containing the file.
    - Run the following command:

    ```bash
    python farefinale.py
    ```

    - This will start the API on `http://localhost:5000/predict`.

3. **Send a prediction request:**
    - Use a tool like Postman or curl to send a POST request to `http://localhost:5000/predict` with the following JSON data:

    ```json
    {
        "product_name": "Apple",
        "demand": "Medium",
        "season": "Summer"
    }
    ```

    - Replace "Apple" with the desired product name, "Medium" with the demand level (Low, Medium, High), and "Summer" with the season (Spring, Summer, Autumn, Winter).

4. **Response:**
    - The API will respond with a JSON object containing the predicted price or an error message if the model is not trained for the specified product.

### Example Response (Success)

```json
{
    "predicted_price": 12.50
}
```

### Example Response (Error)

```json
{
    "error": "Model not trained for product Pear"
}
```

### Notes

* The API uses a Random Forest Regressor model for prediction.
* The model considers the demand and season when adjusting the predicted price.  
* You can modify the demand and season multipliers in the `predict_price` function to customize the price adjustment logic.

