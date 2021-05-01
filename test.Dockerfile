FROM python:3.9.4 AS builder

COPY requirements.txt requirements.txt

RUN pip install --user --upgrade pip && \
    pip install --user -r requirements.txt && \
    pip install --user pytest requests


FROM python:3.9.4-slim

COPY --from=builder /root/.local /root/.local

RUN apt-get update && \
    apt-get install -y --no-install-recommends libmagic1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /api

ENV PYTHONPATH=/api/app

COPY app app

COPY tests tests

CMD ["python", "-m", "pytest", "-ra", "--color=yes"]
