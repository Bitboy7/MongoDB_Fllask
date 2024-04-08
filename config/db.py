from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def connect_to_mongodb():
    uri = os.getenv('MONGO_URI') # URL de la base de datos

    client = MongoClient(uri) # Conexion a la base de datos

    db = client['test'] # Selecciona la base de datos 'test'

    return db

db = connect_to_mongodb()
