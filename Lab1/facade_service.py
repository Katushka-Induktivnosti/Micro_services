import requests
import json
import flask
import uuid

def proc_get_req():
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
    messages_dict = logserv_resp.json()
    return json.dumps(messages_dict)

def proc_post_req():
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
        messerv_resp = requests.get(
        "{msg}/messages".format(msg=messerv_url)
    )
        status = logserv_resp.status_code
        print('Info received from logging service:', status)
        print('Info received from message service:', messerv_resp.text)
        return app.response_class(status=status)
    except Exception as ex:
        raise(ex)
        flask.abort(400)


logserv_url = "http://127.0.0.1:8080"
messerv_url = "http://127.0.0.1:8081"

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