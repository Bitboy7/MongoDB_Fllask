

![cookbookie](static/img/logo.png)
```markdown

# CookBookie

## Descripción del proyecto.

Este proyecto es un blog desarrollado con Flask y MongoDB. Permite a los usuarios crear y gestionar publicaciones en el blog. Utiliza una base de datos MongoDB para almacenar la información de las publicaciones y los usuarios.

Además, se ha añadido autenticación con Google API para permitir a los usuarios iniciar sesión con sus cuentas de Google. Esto proporciona una capa adicional de seguridad y facilita el acceso al blog.

## Prerrequisitos

Antes de comenzar, asegúrate de tener lo siguiente instalado:

- Python 3
- Pip (Gestor de paquetes de Python)
- MongoDB
- Un entorno virtual de Python (opcional, pero recomendado. Puedes usar `venv` o `conda`)

## Instalación

1. Clona este repositorio a tu máquina local usando `git clone`.

```
git clone https://github.com/Bitboy7/MongoDB_Fllask```

2. Navega al directorio del proyecto.

```
cd MongoDB_Flask
```
3. (Opcional) Crea y activa un entorno virtual de Python.

python3 -m venv env
source env/bin/activate  # En Windows, usa `env\Scripts\activate````bash


```4. Instala las dependencias necesarias.


*pip install -r requirements.txt*

```
## .env

MONGO_URI='your uri'
CLIENT_SECRET='your google client'
GOOGLE_CLIENT_ID='your google client id'
SECRET_KEY='your secret key'

## Uso

Para iniciar el servidor, ejecuta:

```bash
python main.py
```

Asegúrate de que MongoDB esté funcionando en tu máquina antes de iniciar el servidor.

## Contribuir

Si deseas contribuir al proyecto, por favor revisa las [guías de contribución](CONTRIBUTING.md).

## Licencia

Este proyecto está licenciado bajo [MIT](LICENSE).

Codix 2024.
