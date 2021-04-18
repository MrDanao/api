FROM python:3.9.4

WORKDIR /api

ENV PYTHONPATH=/api/app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install pytest requests

COPY app app
COPY tests tests

CMD ["pytest", "-ra", "--color=yes"]
