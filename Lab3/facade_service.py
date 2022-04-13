import requests
import json
import flask
import uuid
import random

def proc_get_req():
    port = str(8080+random.randint(1,3))
    logserv_url = f"http://127.0.0.1:%s"%port
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
        "{msg}/messages".format(msg=messerv_url)
    )
    print('Info received from message service:', messerv_resp.text)
    return logserv_resp.text

def proc_post_req():
    port = str(8080+random.randint(1,3))
    logserv_url = f"http://127.0.0.1:%s"%port
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
        messerv_resp = requests.get(
        "{msg}/messages".format(msg=messerv_url)
        )
        print('Info received from message service:', messerv_resp.text)
        return app.response_class(status=status)
    except Exception as ex:
        raise ex
        flask.abort(400)

messerv_url = "http://127.0.0.1:81"

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
