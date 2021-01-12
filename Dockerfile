FROM python:3.6-slim-buster

MAINTAINER giobart

ADD . /code
WORKDIR /code

RUN pip install -r requirements.txt

EXPOSE 5005

ENV MONGO_DB_USERNAME=username

ENV MONGO_DB_PASSWORD=password

CMD ["gunicorn", "-c", "gunicorn_config.py", "entry:app"]

