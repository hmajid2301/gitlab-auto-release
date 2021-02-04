FROM python:alpine3.7
LABEL MAINTAINER="Haseeb Majid me@haseebmajid.dev"
LABEL VERSION="4.0.4"

COPY dist ./dist/
RUN pip install dist/*
