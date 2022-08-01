FROM python:3.10-slim

ARG PIP_FLAGS
ENV PIP_FLAGS=${PIP_FLAGS}

WORKDIR /stimulus

COPY requirements.txt requirements.txt

RUN pip install $PIP_FLAGS -r requirements.txt

COPY . .

RUN ["chmod","+x","run.sh"]

CMD ["./run.sh"]
