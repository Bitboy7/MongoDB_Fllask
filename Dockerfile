# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

CMD [ "python3", "-m" ,"src/main.py", "--host=0.0.0.0"]