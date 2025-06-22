FROM python:3.14.0b3-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000