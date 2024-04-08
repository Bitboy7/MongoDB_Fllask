from flask import Flask, render_template, request, make_response, redirect, abort, session, redirect, url_for
import oauthlib
import os
from gridfs import GridFS
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from config.db import db
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import requests
import pathlib
from dotenv import load_dotenv
import google.auth.transport.requests
# Cargar las variables de entorno desde el archivo .env
load_dotenv()
# Declaramos la variable de ejecución de la aplicación
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app.secret_key = os.getenv('SECRET_KEY')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

# inicio de sesion con google
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
            ],
    redirect_uri="https://cook.up.railway.app/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.errorhandler(oauthlib.oauth2.rfc6749.errors.AccessDeniedError)
def handle_access_denied_error(error):
    return "Access Denied", 403

# Login con Google ------------------------------


@app.route("/glogin")
def glogin():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    # Obtener info de la sesion
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["family_name"] = id_info.get("family_name")
    session["email"] = id_info.get("email")
    session["picture"] = id_info.get("picture")
    session["locale"] = id_info.get("locale")

    # Buscar el usuario en la base de datos
    existing_user = db.users.find_one(
        {"email": session["email"], "google_id": session["google_id"]})

    if existing_user:
        # Actualizar la fecha de creación del usuario existente
        db.users.update_one({"_id": existing_user["_id"]}, {
                            "$set": {"created_at": datetime.now()}})
    else:
        # Guardar la información del usuario en la base de datos de MongoDB
        user_data = {
            "google_id": session["google_id"],
            "name": session["name"],
            "family_name": session["family_name"],
            "email": session["email"],
            "picture": session["picture"],
            "locale": session["locale"],
            "created_at": datetime.now(),
            # Campo para la fecha de primer inicio de sesión
            "first_login_date": datetime.now()
        }
        db.users.insert_one(user_data)

    return redirect("/protected_area")


@app.route('/protected_area')
@login_is_required
def protected_area():
    # Obtener info del usuario desde la sesión
    name = session.get("name")
    email = session.get("email")
    picture = session.get("picture")

    # Renderiza los datos y la platilla
    return render_template("dashboard.html", name=name, email=email, picture=picture)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
# Fin de login con Google ------------------------------


# Rutas de la aplicación ------------------------------
@app.route('/')
def index():
    return render_template('login.html')


@app.route('/publicaciones')
def publicaciones():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' in request.files:
        pdf_file = request.files['pdf']
        if pdf_file.filename != '':
            filename = pdf_file.filename.replace(
                ' ', '_')
            guardar_archivo(pdf_file)  # Guarda el archivo PDF
            guardar_post(filename, request.form['title'], session.get(
                "name"), request.form['description'])

    if 'mp4' in request.files:
        mp4_file = request.files['mp4']
        if mp4_file.filename != '':
            filename = mp4_file.filename.replace(
                ' ', '_')
            guardar_archivo(mp4_file)  # Guarda el archivo MP4
            guardar_post(filename, request.form['title'], session.get(
                "name"), request.form['description'])

    return redirect('/archivos')


@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    # Buscar el archivo en la base de datos
    file = fs.find_one({'filename': filename})
    if file:
        # Crear una respuesta con el contenido del archivo
        response = make_response(file.read())
        # Establecer el encabezado de disposición de contenido para forzar la descarga
        response.headers.set('Content-Disposition',
                             'attachment', filename=filename)
        # Establecer el tipo de contenido como octet-stream para evitar la conversión a HTML en dispositivos móviles
        response.headers.set('Content-Type', 'application/octet-stream')
        return response
    else:
        return 'El archivo no existe'


@app.route('/comment', methods=['POST'])
def comment():
    filename = request.form['filename']
    comment = request.form['comment']
    name = session.get("name")
    if guardar_comentario(filename, comment, name):
        return redirect('/archivos')
    else:
        return "No se encontró el post con el título especificado."


@app.route('/archivos', methods=['GET'])
def get_files():
    # Obtener la lista de archivos PDF
    pdf_files = obtener_archivos('pdf')
    # Obtener la lista de archivos MP4
    mp4_files = obtener_archivos('mp4')
    name = session.get("name")
    email = session.get("email")
    picture = session.get("picture")
    # Obtener hora actual
    hour = datetime.today().strftime("%H:%M:%S")
    post_info = obtener_posts()
    comments = obtener_comentarios()
    # Renderizar la plantilla 'download.html' y pasar las listas de archivos, comentarios y datos del usuario como argumentos
    return render_template('download.html', pdf_files=pdf_files, mp4_files=mp4_files, name=name, email=email, picture=picture, post_info=post_info, comments=comments, hour=hour)


# Correr servidor con gunicorn -----------------------------------------
if __name__ == '__main__':
    app.run(port=5000)
# Ngrok: ngrok http 5000 --domain=likely-cosmic-mosquito.ngrok-free.app
