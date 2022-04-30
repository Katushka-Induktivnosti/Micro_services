import flask
import pika
import sys
import time
import os
import threading
import requests

msg = []
msg_lock = threading.Lock()

def get_conf(service):
    cluster = []
    conf = (requests.get('http://192.168.111.4:8500/v1/agent/services').json())
    for key in conf:
        if key.find(service) != -1:
            cluster.append(f"http://{conf[key]['Address']}:{conf[key]['Port']}")
    return cluster

rabbitmq = get_conf("rabbitmq")

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/messages', methods=['GET'])

def message():
    global msg
    if len(msg) < 5:
        return "Not enough messages"
    with msg_lock:
        wiped_msg = msg.copy()
        msg.clear()    
    return ','.join(wiped_msg)

    return ','.join(wiped_msg)
    
def queue():
    channel = connection.channel()
    channel.queue_declare(queue='lab5')

    def callback(ch, method, properties, body):
        global msg
        with msg_lock:
            msg.append(body.decode())
        print(" [x] Received %r" % body.decode())
        print (','.join(msg))

    channel.basic_consume(queue='lab5', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    queue_thread = threading.Thread(target = queue)
    queue_thread.start()
    app.run(host='0.0.0.0', port='8081')
    