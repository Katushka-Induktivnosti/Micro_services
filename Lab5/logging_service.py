import flask
import json
import hazelcast
import random
import requests

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def get_conf(service):
    cluster = []
    conf = (requests.get('http://192.168.111.4:8500/v1/agent/services').json())
    for key in conf:
        if key.find(service) != -1:
            cluster.append(f"http://{conf[key]['Address']}:{conf[key]['Port']}")
    return cluster

hz = hazelcast.HazelcastClient( 
        cluster_members=get_conf("hazelcast"))
map = hz.get_map("lab5_map").blocking()

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
        return 


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8081)