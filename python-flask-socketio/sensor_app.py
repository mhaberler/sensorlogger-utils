from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    current_app,
)

from flask_socketio import SocketIO, emit
from random import random
from threading import Lock, Thread
import logging

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
import arrow
import custom
from slconfig import genconfig
from operator import itemgetter

# from flask_sock import Sock


udp_thread = None
udp_thread_lock = Lock()
sl_thread = None
sl_thread_lock = Lock()

app = Flask(__name__)
app.config["SECRET_KEY"] = "donsky!"
app.config["SOCK_SERVER_OPTIONS"] = {"ping_interval": 25}

QRcode(app)

socketio = SocketIO(async_mode="threading")
socketio.init_app(app)


UDP_IP = "127.0.0.1"
UDP_PORT = 5005
slq = queue.Queue()
bleMeta = {}


def udp_job(app):
    wkz = os.environ.get("WERKZEUG_RUN_MAIN")
    app.logger.info(f"udp_job: {wkz=}")

    # if wkz == "true":
    #     return
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
    wkz = os.environ.get("WERKZEUG_RUN_MAIN")
    app.logger.info(f"sl_job: {wkz=}")

    # if wkz == "true":
    #     return
    with app.app_context():
        while True:
            msg = slq.get()
            socketio.emit("udp", msg)


@socketio.on("connect")
def handle_connect():
    print(f"Client connected {request.sid=}")
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


@app.route("/tp")
def teleplot():
    return render_template("teleplot.html")


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")


@app.route("/trackme/<clientsession>/")
def trackme(clientsession=""):
    app.logger.info(f"trackme {clientsession=}")
    return render_template("leaflet.html", clientsession=clientsession)


def decode_ble_beacons(j, debug=False, customDecoder=None):
    global bleMeta
    result = []
    for sample in j:
        if sample["name"].startswith("bluetoothmetadata"):
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
            ret = decodeBLE(input)
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


def teleplotify(samples):
    samples.sort(key=itemgetter("name", "time"))
    for s in samples:
        sensor = s["name"].replace(" ", "_")
        ts = s["time"]
        for key, value in s.items():
            if key == "name":
                continue
            if key == "time":
                continue
            if isinstance(value, float) or isinstance(value, int):
                variable = key.removeprefix("values_")
                tp = {
                    "data": f"{sensor}.{variable}:{value}|np\n",
                    "timestamp": ts / 1.0e6,
                }
                slq.put(tp)


@app.route("/sl/<clientsession>/", methods=["POST"])
def getpos(clientsession=""):
    body = json.loads(request.data)
    messageId = body["messageId"]
    sessionId = body["sessionId"]
    deviceId = body["deviceId"]
    payload = body["payload"]
    # check for test push
    for p in payload:
        if p.get("name", None) == "test":
            app.logger.info(
                f"client hit test: {clientsession=} {messageId=} {sessionId=} {deviceId=}"
            )
            return {}

    result = decode_ble_beacons(payload, debug=False, customDecoder=custom.Decoder)
    flattened = []
    for report in result:
        flattened.append(flatten(report))
    teleplotify(flattened)
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


@app.route("/uplot")
def uplot():
    app.logger.info(f"uplot")
    return render_template("stream-data.html")


@app.route("/")
def index():
    return render_template("index.html")


# @socketio.on("connect")
# def connect():
#     global thread
#     app.logger.info(f"Client connected: {request.sid=}")
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = socketio.start_background_task(udp_thread)


# @socketio.on_error_default
# def default_error_handler(e):
#     app.logger.error(
#         f"on_error_default: {request.event['message']}"
#     )  # "my error event"
#     app.logger.error(f"on_error_default: {request.event['args']}")  # (data,)


"""
Decorator for disconnect
"""


# @socketio.on("disconnect")
# def disconnect():
#     app.logger.error(f"Client disconnected: {request.sid=}")

# app.logger.error(f"{__name__=}")
# if __name__ == "sensor_app":

# if __name__ == "__main__":
# if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
#     thread = Thread(target=udp_thread)
#     thread.daemon = True
#     thread.start()

# if __name__ == "__main__":
#     socketio.run(app)
