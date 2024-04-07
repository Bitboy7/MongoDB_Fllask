# CHEF-BLOG

Descripción del proyecto.

Este proyecto es un blog desarrollado con Flask y MongoDB. Permite a los usuarios crear y gestionar publicaciones en el blog. Utiliza una base de datos MongoDB para almacenar la información de las publicaciones y los usuarios.

Además, se ha añadido autenticación con Google API para permitir a los usuarios iniciar sesión con sus cuentas de Google. Esto proporciona una capa adicional de seguridad y facilita el acceso al blog.

## Instalación

Sigue estos pasos para instalar el proyecto:

1. Clona el repositorio:

```bash
git clone https://github.com/usuario/proyecto.git
cd proyecto

# instalar dependencias
pip install -r requirements.txt

# .env
MONGO_URI='your uri'
CLIENT_SECRET='your google client'
GOOGLE_CLIENT_ID='your google client id'
SECRET_KEY='your secret key'

# Ejecutar
python run.py