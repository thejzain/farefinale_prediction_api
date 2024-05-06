import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("admin.json")  # Path to your service account key file
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()


def upload_data_to_firestore(csv_file_path, collection_name):
    # Read data from CSV file
    with open(csv_file_path, "r") as file:
        reader = csv.DictReader(file)
        data = list(reader)

    # Upload data to Firestore
    for row in data:
        # Add data to Firestore collection
        db.collection(collection_name).add(row)
        print("Data uploaded:", row)


# Call the function with your CSV file path and Firestore collection name
upload_data_to_firestore("your_dataset.csv", "test_ml")
