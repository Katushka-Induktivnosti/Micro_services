import flask
import json
import hazelcast
import random

app = flask.Flask(__name__)
app.config["DEBUG"] = True

hz = hazelcast.HazelcastClient( 
        cluster_members=[
        "192.168.111.1:5701",
        "192.168.111.2:5701",
        "192.168.111.3:5701"
    ])
map = hz.get_map("lab4_map").blocking()

@app.route('/logging', methods=['GET', 'POST'])
def logging_serv():
    if flask.request.method == 'GET':
        return proc_get_req()
    else:
        return proc_post_req()

def proc_post_req():
    data=flask.request.json
    print('Received request: ', data)
    try:
        map.set(data["uuid"], data["msg"])
        print("Saved to hazelcast map")
        return "OK"
    except Exception as ex:
        raise ex
        print('Message cannot be saved to hazelcast map')
        return 500      

def proc_get_req():
    data=flask.request.json
    print('Received request: ', data)
    try:
        print('Return messages: ',  map.values())
        return ','.join(map.get_all(map.key_set()).values())
    except Exception as ex:
        raise ex
        return 400


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8081)