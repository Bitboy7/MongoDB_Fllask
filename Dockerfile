FROM python:3.10.8-slim-buster
WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
EXPOSE 80
CMD ["gunicorn", "src.main:app", "-b", "0.0.0.0:80"]
