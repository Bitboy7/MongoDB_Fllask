FROM python:3.10.8-slim-buster
ADD . /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 80
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
