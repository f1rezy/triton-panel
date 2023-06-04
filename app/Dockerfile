FROM python:3.11-slim

WORKDIR /app

MAINTAINER "Yurkov Vladislav <yurk0v-vl@yandex.ru>"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt
# copy project
COPY . .


EXPOSE 5000