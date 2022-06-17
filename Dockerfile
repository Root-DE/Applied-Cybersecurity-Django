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

COPY setup.sh /setup/setup.sh
RUN chmod +x /setup/setup.sh
COPY healthcheck.sh /healthcheck.sh
HEALTHCHECK CMD ["bash", "/healthcheck.sh"] # runs every 30 seconds by default
#HEALTHCHECK CMD ["django-admin", "check"] # runs every 30 seconds by default

## wait for DB to open TCP Port, configured via Environment Variable according to the docs of docker-compose-wait
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

CMD /wait && /setup/setup.sh

WORKDIR /

COPY ./src /

