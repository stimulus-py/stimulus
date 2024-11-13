FROM python:3.10-slim
ARG UID
ARG GID

ARG PIP_FLAGS
ENV PIP_FLAGS=${PIP_FLAGS}

WORKDIR /stimulus

COPY requirements.txt requirements.txt

RUN addgroup --gid $GID nonroot && \
    adduser --uid $UID --gid $GID --disabled-password --gecos "" nonroot && \
    pip install $PIP_FLAGS -r requirements.txt && \
    chown nonroot:nonroot /stimulus

COPY --chown=nonroot:nonroot . .

USER nonroot

RUN ["chmod","+x","run.sh"]

CMD ["./run.sh"]
