FROM python:slim AS builder

RUN apt update && \
    apt install -y libpq-dev gcc

# create a virutal environment 
RUN python -m venv /opt/venv
# Activate the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# Operational Stage
FROM python:slim

RUN apt update && \
    apt install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Get the virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /

COPY ./src /