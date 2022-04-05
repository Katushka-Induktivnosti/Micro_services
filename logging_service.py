import flask
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True

messages_dict = {}


@app.route('/logging', methods=['GET', 'POST'])
def facade_serv():
    if flask.request.method == 'GET':
        return proc_get_req()
    else:
        return proc_post_req()

def proc_post_req():
    data=flask.request.json
    print('Received request: ', data)
    messages_dict.update({data["uuid"]: data["msg"]})
    print('Saved to log array')
    return "ok"

def proc_get_req():
    print('Return messages: ', messages_dict.values())
    return json.dumps([msg for msg in messages_dict.values()])

@app.route('/messages')
def messages():
    return 'Service was not implemented yet'


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8080)