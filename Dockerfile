FROM docker.io/alpine:3.20.0

MAINTAINER Jules Stähli <jules.stahli@gmail.com>

WORKDIR /home/mailman3_exporter

ENV PYTHONUNBUFFERED=1

COPY  ["./mailman3_exporter", "./mailman_exporter.py", "./requirements.txt", "./"]

RUN apk add --update --no-cache python3 py-pip \
    && ln -sf python3 /usr/bin/python \
    && pip3 install --break-system-packages -r requirements.txt

EXPOSE 9934

ENTRYPOINT ["python3", "mailman_exporter.py"]
