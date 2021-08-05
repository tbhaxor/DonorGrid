FROM python:3-alpine3.14

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add gcc musl-dev libffi-dev postgresql postgresql-dev rust cargo nginx git

COPY . .
RUN pip install -U pip
RUN pip install -r requirements.txt

RUN git init && \
    git clean -Xdf && \
    rm -rf .gitignore .git

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]