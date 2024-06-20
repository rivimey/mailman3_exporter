FROM docker.io/alpine:3.20.0

MAINTAINER Jules Stähli <jules.stahli@gmail.com>

WORKDIR /home

ENV PYTHONUNBUFFERED=1

COPY ./mailman3_exporter mailman3_exporter

RUN apk add --update --no-cache python3 py-pip \
    && ln -sf python3 /usr/bin/python \
    && cd mailman3_exporter \
    && pip3 install --break-system-packages -r requirements.txt

WORKDIR /home/mailman3_exporter

EXPOSE 9934

ENTRYPOINT ["python3", "mailman_exporter.py"]
