FROM python:3

LABEL maintainer="Egehan Gündoğdu <egehn.gundogdu@gmail.com>"
ENV PYTHONBUFFERED 1 



COPY ./requirements.txt /requirements.txt 
COPY ./.pylintrc /.pylintrc
RUN pip install -r requirements.txt


RUN mkdir /app

WORKDIR /app

COPY ./app /app

