from flask import (
    Flask,
    abort,
    render_template,
    request,
    current_app,
    url_for,
    flash,
    redirect,
)

from flask_socketio import SocketIO, emit, Namespace
from threading import Lock, Thread

from datetime import datetime
import json
from flask_qrcode import QRcode
import shortuuid

# from celery import Celery
import socket, select, queue
import os, time

# from flask_cors import CORS
from TheengsDecoder import decodeBLE
from flatten_json import flatten
import custom
from slconfig import genconfig, merge, gen_export_code
from operator import itemgetter
from collections import defaultdict

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, RadioField
from wtforms.validators import InputRequired, Length

sessions = {}
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
slq = queue.Queue()
bleMeta = {}
SESSION_TIMEOUT = 60

udp_thread = None
udp_thread_lock = Lock()
sl_thread = None
sl_thread_lock = Lock()

app = Flask(__name__)
app.config["SOCK_SERVER_OPTIONS"] = {"ping_interval": 25}
app.config["UPLOAD_FOLDER"] = "/tmp/sensorlogger-upload"
app.config["SECRET_KEY"] = "yo2Ecuugh8oowiep1rui0niev8Fahnoh"

QRcode(app)

socketio = SocketIO(async_mode="threading")
socketio.init_app(app)


def udp_job(app):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
    udp_socket.bind((UDP_IP, UDP_PORT))
    last_id = 0
    with app.app_context():
        while True:
            data, addr = udp_socket.recvfrom(1024)  # buffer size is 1024 bytes
            last_id += 1
            msg = {
                "data": data.decode(),
                # "fromSerial": False,
                "timestamp": time.time(),
            }
            socketio.emit("udp", msg)
            # socketio.emit('new_alerts', {'msg': 'New alert', 'id': last_id}, namespace='/rt/notifications/')


def sl_job(app):
    with app.app_context():
        while True:
            msg = slq.get()
            socketio.emit("udp", msg)


@socketio.on("message")
def handle_message(data):
    app.logger.info(f"received message: {data=} {request.sid=}")
    msg = json.loads(data)

    s = msg.get("session", None)
    session = sessions.get(s, None)
    if session:
        pass
        # create queue
        # start sl_job relay thread
        # confirm

class MyCustomNamespace(Namespace):
    def on_connect(self):
        app.logger.info(f"{self.namespace=} on_connect")

    def on_disconnect(self):
        app.logger.info(f"{self.namespace=} on_disconnect")

    def on_message(self, m):
        app.logger.info(f"{self.namespace=} on_message {m}")

    def on_error(self):
        app.logger.info(f"{self.namespace=} on_error")

    def on_my_event(self, data):
        emit('my_response', data)

socketio.on_namespace(MyCustomNamespace('/test'))

@socketio.on("connect")
def handle_connect(auth):
    app.logger.info(f"Client connected {request.sid=}")
    return
    # emit("udp", {"message": "foobar"}, broadcast=True)
    global udp_thread
    with udp_thread_lock:
        if udp_thread is None:
            udp_thread = socketio.start_background_task(
                udp_job, current_app._get_current_object()
            )
    global sl_thread
    with sl_thread_lock:
        if sl_thread is None:
            sl_thread = socketio.start_background_task(
                sl_job, current_app._get_current_object()
            )


@app.route("/trackme/<clientsession>/")
def trackme(clientsession=""):
    app.logger.info(f"trackme {clientsession=}")
    return render_template("leaflet.html", sessionId=clientsession)


def decode_ble_beacons(j, debug=False, customDecoder=None):
    global bleMeta
    result = []
    for sample in j:
        if sample["name"].startswith("bluetoothmetadata"):
            app.logger.info(f"bluetoothmetadata: '{sample}'")

            ssuids = sample["values"].get("serviceUUIDs", [])
            if not isinstance(ssuids, list):
                # mutate so we always have a list of serviceUUIDs
                sample["values"]["serviceUUIDs"] = [ssuids]
            id = sample["values"]["id"]
            sid = "bluetooth-" + id.replace(":", "")
            bleMeta[sid] = sample
            continue
        meta = bleMeta.get(sample["name"], None)
        if meta and "manufacturerData" in sample["values"]:
            # see https://github.com/theengs/decoder/blob/development/examples/python/ScanAndDecode.py
            data = {}
            meta_val = meta.get("values", {})
            localName = meta_val.get("localName", None)
            if not localName:
                localName = meta_val.get("name", None)
            if localName:
                data["name"] = localName
            suuids = meta_val.get("serviceUUIDs", [])
            if suuids:
                sl = suuids[0]
                if len(sl) > 4:
                    sl = sl[4:8]
                data["servicedatauuid"] = sl
            data["id"] = sample["values"]["id"]
            data["time"] = sample["time"]
            data["rssi"] = sample["values"]["rssi"]
            data["manufacturerdata"] = sample["values"]["manufacturerData"]
            input = json.dumps(data)
            app.logger.info(f"data sent to decoder: '{input}'")
            # input = '{"servicedatauuid": "181b", "servicedata": "0224b2070113100c08fdff4a0b", "manufacturerdata": "5701381ec781c63c", "name": "MIBFS", "id": "5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28", "rssi": -67}'
            # input = '{"servicedatauuid": "181b", "manufacturerdata": "5701381ec781c63c", "name": "MIBFS", "id": "5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28", "rssi": -67}'
            # {"name": "MIBFS", "servicedatauuid": "181b", "id": "2b79964c-23a6-aba8-ed42-b4351592548d", "time": 1691300324099000000, "rssi": -73, "manufacturerdata": "5701381ec781c63c"}'
            ret = decodeBLE(input)
            #   data sent to decoder:  {"servicedatauuid": "181b", "servicedata": "0224b2070113100c08fdff4a0b", "manufacturerdata": "5701381ec781c63c", "name": "MIBFS", "id": "5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28", "rssi": -67}
            # TheengsDecoder found device: {"servicedatauuid":"181b","servicedata":"0224b2070113100c08fdff4a0b","manufacturerdata":"5701381ec781c63c","name":"MIBFS","id":"5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28","rssi":-67,"brand":"Xiaomi","model":"Mi Body Composition Scale","model_id":"XMTZC02HM/XMTZC05HM","type":"SCALE","weighing_mode":"person","unit":"kg","weight":14.45}
            if ret:
                js = json.loads(ret)
                js.pop("id", None)
                js.pop("mfid", None)
                js.pop("manufacturerdata", None)
                js.pop("servicedatauuid", None)
                result.append(js)
                continue

            if customDecoder:
                ret = customDecoder(data, debug)
                if ret:
                    result.append(ret)
                    continue
        result.append(sample)
    return result


# myValue:1627551892444:1;1627551892555:2;1627551892666:3

# https://stackoverflow.com/questions/50505381/python-split-a-list-of-objects-into-sublists-based-on-objects-attributes


def teleplotify(samples, q):
    # samples.sort(key=itemgetter("name", "time"))
    # d = defaultdict(list)
    # for item in samples:
    #     d[item['name']].append(item)
    # for name, vlist in d.items():
    #     vname = f"{name}.",
    #     for v in vlist:
    #         for key, value in v.items():
    #             if key == "name":
    #                 continue
    #             if key == "time":
    #                 vtime = value
    #                 continue
    ts = time.time()  # default to receive time
    for s in samples:
        sensor = s["name"].replace(" ", "_")
        for key, value in s.items():
            if key == "name":
                continue
            if key == "time":
                ts = s["time"] / 1.0e6
                continue
            if isinstance(value, float) or isinstance(value, int):
                variable = key.removeprefix("values_")
                tp = {
                    "data": f"{sensor}.{variable}:{ts}:{value}|np\n",
                    # "timestamp": ts ,
                }
                q.put(tp)


# curl -X POST http://172.16.0.212:5010/token -H "Accept: application/json" -H "Authorization: Bearer blahfasel"

# @app.route("/token", methods=["POST"])
# def gettoken():
#     app.logger.info(f"{request.headers=}")
#     return {"foo": 123}


@app.route("/sl/<clientsession>", methods=["POST"])
def getpos(clientsession=""):
    try:
        body = json.loads(request.data)
        messageId = body["messageId"]
        sessionId = body["sessionId"]
        deviceId = body["deviceId"]
        payload = body["payload"]
        bearer = request.headers.get("Authorization")
        token = bearer.split()[1]
    except Exception:
        return f"invalid request", 404

    if not clientsession in sessions:
        return "no such session: {clientsession}", 404

    if sessions[clientsession]["authToken"] != token:
        return f"invalid token: {token}", 404

    age = int(time.time() - sessions[clientsession]["created"])
    if age > SESSION_TIMEOUT:
        return f"Session timed out - link age is {age} seconds", 404

    # check for test push
    for p in payload:
        if p.get("name", None) == "test":
            app.logger.info(
                f"client test push: {clientsession=} {messageId=} {sessionId=} {deviceId=}"
            )
            return {}

    if not "deviceId" in sessions[clientsession]:
        sessions[clientsession]["deviceId"] = deviceId

    if not "queue" in sessions[clientsession]:
        app.logger.info(f"no queue for {clientsession}")
        return {}

    # record last messageId
    sessions[clientsession]["messageId"] = messageId

    result = decode_ble_beacons(payload, debug=False, customDecoder=custom.Decoder)
    flattened = []
    for report in result:
        flattened.append(flatten(report))
    teleplotify(flattened, slq)
    return {}


@app.route("/livetrack", methods=["GET", "POST"])
def livetrack():
    clientsession = shortuuid.uuid()
    secret = shortuuid.uuid()
    authToken = f"realm={secret}"
    uri = f"{request.host_url}sl/{clientsession}"
    config = genconfig(uri, authToken=authToken)
    app.logger.info(f"generate config: {clientsession=} {secret=} {config=}")
    return render_template(
        "genqrcode.html", config=config, tracker=f"/trackme/{clientsession}/"
    )



@app.route("/plot", methods=["GET", "POST"])
def plot():
    app.logger.info(f"plot {request.method=}")
    if request.method == "GET":
        return render_template("plot.html")
    if request.method == "POST":
        app.logger.info(f"locationRate: {request.form.getlist('locationRate')}")
        app.logger.info(f"accelRate: {request.form.getlist('accelRate')}")
        app.logger.info(f"baroRate: {request.form.getlist('baroRate')}")
        app.logger.info(f"sensors: {request.form.getlist('sensors')}")
        app.logger.info(f"to_dict: {request.form.to_dict(flat=False)}")

        sessionKey = shortuuid.uuid()
        authToken = shortuuid.uuid()
        url = request.host_url + "sl/" + sessionKey
        sessions[sessionKey] = {
            "authToken": authToken,
            "created": time.time(),
            "url": url,
        }
        params = {
            "http": {
                "enabled": True,
                "url": url,
                "batchPeriod": 1000,
                "authToken": "Bearer " + authToken,
            },
        }
        cfg = merge(request, params)
        return render_template(
            "genqrcode.html", config=gen_export_code(cfg), tracker=f"/tp?session={sessionKey}"
        )
    return {}


@app.route("/tp")
def teleplot():
    s = request.args.get('session')
    app.logger.info(f"/tp: session={s}")
    return render_template("teleplot.html", clientsession=s)

@app.route("/")
def index():
    return render_template("index.html")


@socketio.on_error_default
def default_error_handler(e):
    app.logger.error(
        f"on_error_default: {request.event['message']}"
    )  # "my error event"
    app.logger.error(f"on_error_default: {request.event['args']}")  # (data,)


@socketio.on("disconnect")
def disconnect():
    app.logger.error(f"Client disconnected: {request.sid=}")


# receive a JSON file by upload
# convert as per options
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
