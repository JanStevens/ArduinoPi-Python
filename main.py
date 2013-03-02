from flask import Flask
from flask import Response
from flask import json
from flask import request
from arduino_pi import ArduinoPi
import os
import sys
import pprint

app = Flask(__name__)

# so random
HIGH = 255
LOW = 0
MEGA2560 = 100
UNO = 101
LEONARDO = 102
ADK = 103

arduinopi = ArduinoPi(MEGA2560)

@app.route('/api/', methods= ['POST'])
def api_root():

    if 'mode' in request.form:
        mode = request.form['mode']
    else:
        data = { 'state' : 'failed', 'error' : 'No mode selected in POST request'}
        js = json.dumps(data)
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    if 'data' in request.form:
        data = request.form['data']
    else:
        data = 0

    try:
        val = arduinopi.process(mode, data)
        data = {'state' : 'success', 'result': val}

    except:
        e = sys.exc_info()[1]
        data = { 'state' : 'failed', 'error' : str(e).capitalize()}

    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    return resp



@app.route('/api/<path:path>', methods= ['GET'])
def path(path=''):
    path = '/' + path
    path_array = path.split('/')
    mode = path_array[1].lower()

    data = path_array[2:]
    try:
        val = arduinopi.process(mode, data)
        data = {'state' : 'success', 'result': val}
    except:
        e = sys.exc_info()[1]
        data = { 'state' : 'failed', 'error' : str(e).capitalize()}

    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))

    if port == 5000:
        app.debug = True

    app.run(host='0.0.0.0', port = port)


