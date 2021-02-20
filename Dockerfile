FROM python:3.8.8-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache \
    build-base cairo-dev cairo cairo-tools \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
    # for lxml
    gcc libc-dev libxml2-dev libxslt-dev libressl-dev\
    # for cryptography
    gcc musl-dev python3-dev libffi-dev openssl-dev cargo

ADD . /app
WORKDIR /app
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt &&\
    mkdir -p /app/out

VOLUME /app/out
ENTRYPOINT python3 main.py
