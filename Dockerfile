FROM python:3.10.8-slim-buster
ADD . /app
WORKDIR /app/src
RUN pip install -r requirements.txt
EXPOSE 80
CMD py main.py