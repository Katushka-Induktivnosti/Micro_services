import requests
import json
import flask
import uuid
import random
import pika

def proc_get_req():
    port_l = str(8080+random.randint(1,3))
    port_m = str(80+random.randint(1,2))
    messerv_url = "http://127.0.0.1:%s"%port_m
    logserv_url = "http://127.0.0.1:%s"%port_l
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
    port_l = str(8080+random.randint(1,3))
    logserv_url = "http://127.0.0.1:%s"%port_l
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

        connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='lab4')

        channel.basic_publish(exchange='', routing_key='lab4', body=flask.request.json.get('msg'))
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

app.run(host='0.0.0.0', port='80')