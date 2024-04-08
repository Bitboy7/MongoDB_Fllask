from config.db import *
from gridfs import GridFS
from datetime import datetime
import main as app
import os
from werkzeug.utils import secure_filename

fs = GridFS(db) # Crear un sistema de archivos en la base de datos

def guardar_archivo(file):
    # Obtener la fecha y hora actual
    fecha_actual = datetime.today()
    
    # Reemplazar espacios en el nombre de archivo por _
    filename = secure_filename(file.filename.replace(" ", "_"))
    
    # Guardar el archivo en la carpeta uploads dentro de static
    file.save(os.path.join(app.config.get('UPLOAD_FOLDER', 'src/static/uploads'), filename))
    
    # Guardar el archivo en el sistema de archivos de la base de datos
    fs.put(file, filename=filename, fecha_creacion=fecha_actual)
    

def obtener_archivos(extension):
    # Utiliza la función find de la variable fs para buscar archivos con la extensión especificada
    files = fs.find({'filename': {'$regex': f'\.{extension}$'}})
    return files


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


def guardar_comentario(filename, comment, name):
    # Obtener la fecha y hora actual
    fecha_actual = datetime.today().strftime("%d-%m-%Y %H:%M:%S")
    
    # Obtener el usuario que publica el comentario
    author = db.users.find_one({"name": name})
    
    if author:
        # Obtener el post_id basado en el filename
        post_id = obtener_post_id(filename)
        
        if post_id:
            # Guardar la información del comentario en la colección "comentarios" relacionándolo al post
            comment_data = {
                "post_id": post_id,
                "comment": comment,
                "author": author["_id"],
                "fecha_creacion": fecha_actual
            }
            db.comentarios.insert_one(comment_data)
            return True
        else:
            print("No se encontró el post con el filename especificado.")
            return False
    else:
        print("No se encontró el usuario que publica el comentario.")
        return False


def obtener_post_id(filename):
    # Obtener el post_id basado en el título del post
    post = db.posts.find_one({"filename": filename})
    if post:
        return post["_id"]
    else:
        print("No se encontró el post con el título especificado.")
        return None
            
            
def obtener_posts():
    # Utiliza la función aggregate de la variable db.posts para obtener todos los posts y sus colecciones relacionadas
    posts = db.posts.aggregate([
        {
            '$lookup': {
                'from': 'users',
                'localField': 'author',
                'foreignField': '_id',
                'as': 'author_info'
            }
        },
        {
            '$addFields': {
                'likes': 0  # Agregar el campo 'likes' con un contador inicial de 0
            }
        }
    ])
    
    # Crear una lista de información de cada post
    post_info = [(post['_id'], post['filename'], post['title'], post['author_info'][0]['name'], post['fecha_creacion'], post['likes'], post['description']) for post in posts]
    return post_info

def obtener_comentarios():
    # Utiliza la función aggregate de la variable db.comentarios para obtener todos los comentarios relacionados a un post_id
    comments = db.comentarios.aggregate([
        {
            '$lookup': {
                'from': 'users',
                'localField': 'author',
                'foreignField': '_id',
                'as': 'author_info'
            }
        },
        {
            '$project': {
                'post_id': 1,  # Agregar el campo 'post_id' a la proyección
                'comment': 1,
                'author_name': '$author_info.name',
                'author_picture': '$author_info.picture',
                'author_email': '$author_info.email',
                'fecha_creacion': 1
            }
        }
    ])
    
    # Crear una lista de información de cada comentario
    comment_info = [(comment['_id'], comment['post_id'], comment['comment'], comment['author_name'][0], comment['author_picture'][0], comment['author_email'][0], comment['fecha_creacion']) for comment in comments]
    return comment_info

