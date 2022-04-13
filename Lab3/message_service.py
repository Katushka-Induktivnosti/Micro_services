import flask

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/messages', methods=['POST','GET'])
def message():
    return "Service was not implemented yet"

app.run(host='0.0.0.0', port='81')
