FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

COPY ./pyproject.toml /app/

RUN uv pip install -r pyproject.toml --system

COPY . /app
