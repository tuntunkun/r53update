# Dockerfile
FROM python:3.9-alpine
MAINTAINER Takuya Sawada <takuya@tuntunkun.com>

ARG AWS_ACCESS_KEY
ARG AWS_SECRET_KEY
ARG AWS_REGION

ENV AWS_ACCESS_KEY_ID ${AWS_ACCESS_KEY}
ENV AWS_SECRET_ACCESS_KEY ${AWS_SECRET_KEY}
ENV AWS_DEFAULT_REGION ${AWS_REGION}

ADD setup.py /usr/src
ADD r53update /usr/src/r53update

RUN apk add --virtual .build-deps gcc python3-dev musl-dev linux-headers

RUN pip install --upgrade pip
RUN pip install /usr/src

RUN apk del --purge .build-deps

RUN rm -rf /usr/src/* /var/apk/cache/*

ENTRYPOINT ["r53update"]
