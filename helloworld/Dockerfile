FROM python:3.12-slim AS base

WORKDIR /srujan

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt /srujan
RUN pip install -r requirements.txt

COPY . /srujan

EXPOSE 8000

CMD ["gunicorn", "helloworld.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]