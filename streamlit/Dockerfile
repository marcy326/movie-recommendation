FROM python:3.11.4-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
