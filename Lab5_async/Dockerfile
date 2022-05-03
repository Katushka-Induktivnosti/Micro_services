FROM python:latest
LABEL node_number="Logging"

WORKDIR /usr/app/src
COPY main.py ./
COPY config.json ./
COPY startup.sh ./
RUN ["python", "-m", "pip", "install", "hazelcast-python-client"]
RUN ["python", "-m", "pip", "install", "aiohttp"]
RUN ["python", "-m", "pip", "install", "pika"]
RUN ["python", "-m", "pip", "install", "requests"]
RUN ["apt", "install", "curl"]
CMD ["./startup.sh"]
