FROM python:3.12.6-alpine3.19

### install packages
RUN apk update && \
    apk add curl git bash nano && \
    apk add --virtual build-deps gcc musl-dev && \
    apk add --no-cache mariadb-dev && \
    rm -rf /var/cache/apk/*

### Install Python dependencies
COPY requirements.txt /app/
WORKDIR /app/
RUN pip install -r requirements.txt

### add user and group
RUN addgroup helper && adduser -SG helper helper
RUN chown -R tgads:tgads /usr/local/lib/python3.12/site-packages

### Copy files
COPY . /app/

RUN chown -R helper:helper /app

USER helper
