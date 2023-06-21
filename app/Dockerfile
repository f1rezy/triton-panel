FROM python:3.11

# set work directory
WORKDIR /app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN pip install --upgrade pip

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .


EXPOSE 8000