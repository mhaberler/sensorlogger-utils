from flask import Flask, render_template, request, current_app, url_for, flash, redirect

from flask_socketio import SocketIO, emit
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


UDP_IP = "127.0.0.1"
UDP_PORT = 5005
slq = queue.Queue()
bleMeta = {}


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


@app.route("/trackme/<clientsession>/")
def trackme(clientsession=""):
    app.logger.info(f"trackme {clientsession=}")
    return render_template("leaflet.html", clientsession=clientsession)


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


def teleplotify(samples):
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
        params = {
            "http": {
                "enabled": True,
                "url": "http://172.16.0.212:5010/sl/6Qss2oWAHxwtoc4fuH7e4d",
                "batchPeriod": 1000,
                "authToken": "realm=WW4yxcg9NJykavqPYmwXEf",
            },
        }
        cfg = merge(request, params)
        return render_template(
            "genqrcode.html", config=gen_export_code(cfg), tracker=f"/tp"
        )
    return {}


# https://www.digitalocean.com/community/tutorials/how-to-use-web-forms-in-a-flask-application
messages = [
    {"title": "Message One", "content": "Message One Content"},
    {"title": "Message Two", "content": "Message Two Content"},
]


@app.route("/formtest")
def formtest():
    return render_template("formtest.html", messages=messages)


@app.route("/create/", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        elif not content:
            flash("Content is required!")
        else:
            messages.append({"title": title, "content": content})
            return redirect(url_for("index"))

    return render_template("create.html")


courses_list = [
    {
        "title": "Python 101",
        "description": "Learn Python basics",
        "price": 34,
        "available": True,
        "level": "Beginner",
    }
]

from forms import CourseForm


@app.route("/wtform", methods=("GET", "POST"))
def wtform():
    form = CourseForm()
    if form.validate_on_submit():
        courses_list.append(
            {
                "title": form.title.data,
                "description": form.description.data,
                "price": form.price.data,
                "available": form.available.data,
                "level": form.level.data,
            }
        )
        return redirect(url_for("wtcourses"))
    return render_template("wtform.html", form=form)


@app.route("/wtcourses/")
def courses():
    return render_template("wtcourses.html", courses_list=courses_list)


@app.route("/")
def index():
    return render_template("index.html")


# receive a JSON file by upload
# convert as per options
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")


@socketio.on_error_default
def default_error_handler(e):
    app.logger.error(
        f"on_error_default: {request.event['message']}"
    )  # "my error event"
    app.logger.error(f"on_error_default: {request.event['args']}")  # (data,)


@socketio.on("disconnect")
def disconnect():
    app.logger.error(f"Client disconnected: {request.sid=}")
