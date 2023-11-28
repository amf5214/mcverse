# syntax=docker/dockerfile:1

FROM --platform=amd64 python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 5000

COPY . .

# configure the container to run in an executed manner
ENTRYPOINT [ "python3" ]

CMD ["app.py" ]

