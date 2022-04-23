import flask
import pika
import sys
import time
import os
import threading

app = flask.Flask(__name__)
app.config["DEBUG"] = True

msg = []

@app.route('/messages', methods=['GET'])

def message():
    data=flask.request.json['msg']
    def ret_func():
        if flask.request.method == 'GET':
            return ','.join(msg)
    def queue():
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='lab4')

        def callback(ch, method, properties, body):
            print(" [x] Received %r" % body.decode())
            msg.append(body.decode())
            print (','.join(msg))

        channel.basic_consume(queue='lab4', on_message_callback=callback, auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    t1 = threading.Thread(target = queue)
    t1.start()

    t2 = threading.Thread(target=ret_func)
    t2.start()
    t2.join()
    return ','.join(msg)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='81')
    