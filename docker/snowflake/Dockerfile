FROM python:3.8-slim

RUN apt-get update
RUN apt-get install -y git

COPY requirements.txt requirements-extra.txt requirements-s3.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN pip install -r /tmp/requirements-s3.txt
RUN pip install -r /tmp/requirements-extra.txt
RUN pip install sql-runner

ENTRYPOINT ["sqlrunner"]
