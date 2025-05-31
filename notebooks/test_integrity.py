import pandas as pd
from pymongo import MongoClient
import os

def get_db_data():
    client = MongoClient(os.environ['MONGO_URI'])
    db = client[os.environ['MONGO_DB']]
    collection = db[os.environ['MONGO_COLLECTION']]
    return pd.DataFrame(list(collection.find({}, {'_id': 0})))

def get_csv_data():
    return pd.read_csv(os.environ["CSV_PATH"])

def test_row_count():
    df_csv = get_csv_data()
    df_mongo = get_db_data()
    assert len(df_csv) == len(df_mongo), "Différence de lignes entre CSV et MongoDB"

def test_columns_match():
    df_csv = get_csv_data()
    df_mongo = get_db_data()
    assert list(df_csv.columns) == list(df_mongo.columns), "Colonnes différentes"

def test_no_nulls():
    df_csv = get_csv_data()
    df_mongo = get_db_data()
    assert df_csv.isnull().sum().sum() == 0, "Valeurs manquantes dans CSV"
    assert df_mongo.isnull().sum().sum() == 0, "Valeurs manquantes dans MongoDB"

def test_no_duplicates():
    df_csv = get_csv_data()
    df_mongo = get_db_data()
    assert not df_csv.duplicated().any(), "Doublons dans CSV"
    assert not df_mongo.duplicated().any(), "Doublons dans MongoDB"
