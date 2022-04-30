from pyexpat.errors import messages
import requests
import json
import flask
import uuid
import random
import pika

def proc_get_req():
    messages = get_conf("message")
    messerv_url = messages[random.randint(0, 1)]
    loggings = get_conf("logging")
    logserv_url = loggings[random.randint(0, 2)]
    print("GET-request is sent to logging service")
    uuid_generation = {
            "uuid":str(uuid.uuid4()),
            "msg":flask.request.json.get('msg')
        }
    logserv_resp = requests.get(
        "{msg}/logging".format(msg=logserv_url),
        json = uuid_generation
    )
    print('Info received from logging service:', logserv_resp.content)    

    messerv_resp = requests.get(
        "{msg}/messages".format(msg=messerv_url),
        json = uuid_generation
    )
    print('Info received from message service:', messerv_resp.text)
    return messerv_resp.text

def proc_post_req():
    loggings = get_conf("logging")
    logserv_url = loggings[random.randint(0,2)]
    print("POST-request is sent to logging service")
    try:
        uuid_generation = {
            "uuid":str(uuid.uuid4()),
            "msg":flask.request.json.get('msg')
        }
        logserv_resp = requests.post(
            "{msg}/logging".format(msg=logserv_url),
           json = uuid_generation
        )
        status = logserv_resp.status_code
        print('Info received from logging service:', status)

        rabbitmq = get_conf("rabbitmq")

        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq[0]))
        channel = connection.channel()

        channel.queue_declare(queue='lab5')

        channel.basic_publish(exchange='', routing_key='lab5', body=flask.request.json.get('msg'))
        print(f" [x] Sent to message queue: %s"%flask.request.json.get('msg'))
        connection.close()

        return app.response_class()

    except Exception as ex:
        raise ex
        flask.abort(400)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET','POST'])
def facade_serv():
    if flask.request.method == 'GET':
        return proc_get_req()
    elif flask.request.method == 'POST':
        return proc_post_req()
    else:
        flask.abort(405)

def get_conf(service):
    cluster = []
    conf = (requests.get('http://192.168.111.4:8500/v1/agent/services').json())
    for key in conf:
        if key.find(service) != -1:
            cluster.append(f"http://{conf[key]['Address']}:{conf[key]['Port']}")
    return cluster



app.run(host='0.0.0.0', port='80')
