from unittest import mock
import pytest
from datetime import datetime
from unittest.mock import Mock
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pytest
from unittest.mock import MagicMock, patch

load_dotenv()

def connect_to_mongodb():
    uri = os.getenv('MONGO_URI') # URL de la base de datos

    client = MongoClient(uri) # Conexion a la base de datos

    db = client['test'] # Selecciona la base de datos 'test'

    return db

db = connect_to_mongodb()

def guardar_post(filename, title, name, description):
    #  # Obtener la fecha y hora actual
    fecha_actual = datetime.today().strftime("%d-%m-%Y %H:%M:%S")

    # Obtener el usuario que publica el post
    author = db.users.find_one({"name": name})

    if author:
        # Guardar la información del archivo en la colección "posts" relacionándolo al usuario
        post_data = {
            "filename": filename,
            "title": title,
            "author": author["_id"],
            "fecha_creacion": fecha_actual,
            "description": description,
        }
        db.posts.insert_one(post_data)
        return True
    else:
        print("No se encontró el usuario que publica el post.")
        return False

def test_guardar_post():
    # Mock the necessary objects
    filename = "test_file.txt"
    title = "Test Post"
    name = "Test User"
    description = "This is a test post"

    db.users.insert_one = Mock(return_value=None)  # Modify the mock to return None instead of a user object

    # Call the function
    result = guardar_post(filename, title, name, description)

    
