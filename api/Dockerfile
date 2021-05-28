FROM python:3.8-slim

# add user
#RUN adduser --system --group --no-create-home app

COPY . /app
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update 

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt 

