FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN adduser --disabled-password --no-create-home my_user && \
    mkdir -p /app/media && \
    chown -R my_user:my_user /app && \
    chmod -R 755 /app/media

USER my_user
