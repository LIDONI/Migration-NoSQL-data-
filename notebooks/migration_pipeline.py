import os
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv

# Charge les variables d’environnement du .env
load_dotenv(override=True)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION")
CSV_PATH = os.getenv("CSV_PATH")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def import_data_from_csv():
    df = pd.read_csv(CSV_PATH)
    data = df.to_dict(orient="records")
    collection.insert_many(data)
    print(f"{len(data)} documents importés avec succès.")

def read_operations():
    print("\nPatient nommé 'Bobby JacksOn' :")
    patient = collection.find_one({"Name": "Bobby JacksOn"})
    print(patient)

    print("\nPatients ayant une facturation > 15000 :")
    for patient in collection.find({"Billing Amount": {"$gt": 15000}}):
        print(patient)

    print("\nPatients avec résultats 'Abnormal' :")
    for patient in collection.find({"Test Results": "Abnormal"}):
        print(patient)

def update_operations():
    print("\nMise à jour de la condition médicale de Bobby JacksOn :")
    result = collection.update_one(
        {"Name": "Bobby JacksOn"},
        {"$set": {"Medical Condition": "Controlled Hypertension"}}
    )
    print(f"Documents modifiés : {result.modified_count}")

    print("\nAjout de 'Follow-up Required' pour les patients anormaux :")
    result = collection.update_many(
        {"Test Results": "Abnormal"},
        {"$set": {"Follow-up Required": True}}
    )
    print(f"Documents modifiés : {result.modified_count}")

def delete_operations():
    print("\nSuppression du patient nommé 'Luis' :")
    result = collection.delete_one({"Name": "Luis"})
    print(f"Documents supprimés : {result.deleted_count}")

    print("\nSuppression des patients admis en 2020 :")
    result = collection.delete_many({
        "Date of Admission": {
            "$gte": "2020-01-01",
            "$lt": "2021-01-01"
        }
    })
    print(f"Documents supprimés : {result.deleted_count}")

def export_data_to_csv(output_path="data/exported_patients.csv"):
    cursor = collection.find()
    df = pd.DataFrame(list(cursor))

    if "_id" in df.columns:
        df = df.drop(columns=["_id"])

    df.to_csv(output_path, index=False)
    print(f"\nExportation terminée : {len(df)} documents sauvegardés dans '{output_path}'")

if __name__ == "__main__":
    import_data_from_csv()
    read_operations()
    update_operations()
    delete_operations()
    export_data_to_csv()

    