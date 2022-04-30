FROM python:latest
LABEL node_number="Message"

WORKDIR /usr/app/src
COPY message_service.py ./
COPY config.json ./
COPY startup.sh ./
RUN ["python", "-m", "pip", "install", "hazelcast-python-client"]
RUN ["python", "-m", "pip", "install", "flask"]
RUN ["python", "-m", "pip", "install", "pika"]
RUN ["python", "-m", "pip", "install", "requests"]
RUN ["apt", "install", "curl"]
CMD ["./startup.sh"]
