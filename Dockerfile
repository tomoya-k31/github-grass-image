FROM python:3.8.8-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache \
    build-base cairo-dev cairo cairo-tools \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
    # for lxml
    gcc libc-dev libxml2-dev libxslt-dev libressl-dev\
    # for cryptography
    gcc musl-dev python3-dev libffi-dev openssl-dev cargo \
    && \
    # python
    pip install --upgrade pip && \
    mkdir -p /app/out

COPY main.py /app
COPY requirements.txt /app

WORKDIR /app
VOLUME /app/out

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT python3
CMD /app/main.py
