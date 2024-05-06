import requests
import json
from itertools import product

# Define the base URL
base_url = "http://localhost:5000/predict"

# Define product names, demand levels, and seasons
product_names = ["Snickers", "Lays", "Noodles", "Potato Chips", "Bread", "Salted Chips"]
demands = ["High", "Medium", "Low"]
seasons = ["Summer", "Spring", "Autumn", "Winter"]

# Generate all combinations of product names, demand levels, and seasons
combinations = list(product(product_names, demands, seasons))

# Iterate over each combination and make a POST request
for item in combinations:
    payload = {
        "items": [
            {"product_name": item[0], "demand": item[1], "season": item[2]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(base_url, data=json.dumps(payload), headers=headers)
    
    # Print the result
    print("Combination:", item)
    print("Response:", response.json())
    print()
