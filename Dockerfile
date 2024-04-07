# Usa una imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido de tu proyecto al contenedor
COPY . .

# Cambia el directorio de trabajo a /app/src
WORKDIR /app

# Expone el puerto en el que se ejecutará tu aplicación Flask
EXPOSE 80

# Define el comando para ejecutar tu aplicación Flask
CMD ["python", "src/app.py"]