#FROM ubuntu:14.04
FROM olympus_base

COPY . /

RUN apt-get update && \
    apt-get install -y python3 python3-pip git libpq-dev && \
    \
    pip3 install -r requirements.txt

CMD export DB_PASSWORD=$DB_ENV_POSTGRES_PASSWORD && python3 run.py

