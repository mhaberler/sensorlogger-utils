#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, time
from flask import (
    Flask,
    render_template,
    redirect,
    request,
    make_response,
    send_file,
    current_app,
    redirect,
)
from threading import Lock
from flask_sock import Sock,ConnectionClosed
from werkzeug.utils import secure_filename
import io
import json
import ndjson
import geojson
from TheengsDecoder import decodeBLE
import codecs
import custom
from flatten_json import flatten
import arrow
import gengpx
from flask_qrcode import QRcode
from bleads import decode_advertisement
from gentp import Teleplot
import re

app = Flask(__name__)
app.config.from_object(__name__)
app.config["SOCK_SERVER_OPTIONS"] = {"ping_interval": 25}
app.config["UPLOAD_FOLDER"] = "/tmp/sensorlogger-upload"
app.config["SECRET_KEY"] = "yo2Ecuugh8oowiep1rui0niev8Fahnoh"
QRcode(app)
sock = Sock(app)

@sock.route("/teleplot/<clientsession>")
def tp(ws, clientsession=""):
    try:
        while True:
            s = ws.receive()
            msg = json.loads(s)
            app.logger.info(f"/tp/{clientsession=} {msg=}")
            liveplot.add_websocket(clientsession, ws)
    except ConnectionClosed:
        app.logger.info(f"/tp/{clientsession=} closed")
        liveplot.del_websocket(ws)


@sock.route("/waitfor/<clientsession>")
def waitfor(ws, clientsession=""):
    try:
        while True:
            s = ws.receive()
            msg = json.loads(s)
            if "hello" in msg:
                app.logger.info(f"/waitfor/{clientsession} {msg=} ")
            liveplot.add_waitingfor(clientsession, ws)
    except ConnectionClosed as e:
        app.logger.info(f"/waitfor/{clientsession} closed: {e}")
        liveplot.del_waitingfor(clientsession, ws)

import liveplot

liveplot.app = app
# liveplot.sock = sock
# liveplot.restore_sessions()
app.register_blueprint(liveplot.liveplot) #, url_prefix='/liveplot')

ALLOWED_EXTENSIONS = ["json"]

reader = codecs.getreader("utf-8")
decoded = "values"
suffix = "-processed"
metadataNames = ["BluetoothMetadata", "Metadata"]
useless = ["manufacturerData"]
skipKeys = ["seconds_elapsed"]


RE_INT = re.compile(r"^[-+]?([1-9]\d*|0)$")
RE_FLOAT = re.compile(r"^[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?$")


def make_numeric(value):
    if isinstance(value, bytes):
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if RE_INT.match(value):
        return int(value)
    if RE_FLOAT.match(value):
        return float(value)
    return None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def traverse_and_modify(obj, **kwargs):
    debug = kwargs.get("debug", None)
    options = kwargs.get("options", [])
    useless = kwargs.get("useless", [])
    timestamp = kwargs.get("timestamp", [])
    if isinstance(obj, dict):
        for key, value in obj.copy().items():
            if (
                "drop_metadata" in options
                and key == "sensor"
                and value in metadataNames
            ):
                obj.clear()
                return
            if key in useless:
                if debug:
                    app.logger.debug(f"drop {key=}")
                obj.pop(key)
                continue
            if key == "seconds_elapsed" and "drop_bad_timestamps" in options:
                if float(value) < 0.0:
                    if debug:
                        app.logger.debug(f"drop bad seconds_elapsed: {value=}")
                    obj.clear()
                    return
            if key == "time" and "linux_timestamp_float" in timestamp:
                obj[key] = float(value) * 1.0e-6
                continue
            if key == "time" and "linux_timestamp" in timestamp:
                obj[key] = int(value) // 1000000
                continue
            if key == "time" and "iso8061" in timestamp:
                obj[key] = arrow.Arrow.fromtimestamp(float(value) * 1.0e-6).isoformat()
                continue
            if "strings_to_numeric" in options and isinstance(value, str):
                try:
                    obj[key] = int(value)
                except ValueError:
                    try:
                        obj[key] = float(value)
                    except ValueError:
                        pass
                    pass
                    continue

        if isinstance(value, dict):
            traverse_and_modify(value, **kwargs)

    elif isinstance(obj, list):
        for _, value in enumerate(obj):
            traverse_and_modify(value, **kwargs)
    return obj


def decode_ble_beacons(j, debug=False, customDecoder=None):
    bleMeta = {}
    for sample in j:
        if sample["sensor"].startswith("bluetooth-"):
            if "advertisement" in sample:
                da = decode_advertisement(sample["advertisement"])
                # could do this, but ATM not really useful and not JSON serializable
                # sample.update(da)
        if sample["sensor"].startswith("BluetoothMetadata"):
            if not isinstance(sample["serviceUUIDs"], list):
                # mutate so we always have a list of serviceUUIDs
                sample["serviceUUIDs"] = [sample["serviceUUIDs"]]
            id = "bluetooth-" + sample["id"].replace(":", "")
            bleMeta[id] = sample
            continue
        meta = bleMeta.get(sample["sensor"], None)
        if meta and "manufacturerData" in sample:
            # see https://github.com/theengs/decoder/blob/development/examples/python/ScanAndDecode.py
            data = {}
            if meta["name"]:
                data["name"] = meta["name"]
            elif meta["localName"]:
                data["name"] = meta["localName"]
            sl = meta["serviceUUIDs"][0]
            if len(sl) > 4:
                sl = sl[4:8]
            data["servicedatauuid"] = sl
            data["id"] = sample["id"]
            data["rssi"] = sample["rssi"]
            data["manufacturerdata"] = sample["manufacturerData"]
            input = json.dumps(data)
            result = decodeBLE(input)
            if result:
                js = json.loads(result)
                js.pop("id", None)
                js.pop("mfid", None)
                js.pop("manufacturerdata", None)
                js.pop("servicedatauuid", None)
                sample[decoded] = js
                if debug and sample[decoded]:
                    app.logger.debug(json.dumps(sample, indent=2))
                continue

            if customDecoder:
                result = customDecoder(data, debug)
                if result:
                    sample[decoded] = result
                    continue
    return


def teleplotify(samples, options):
    bleMeta = {}
    gen3d = "gen3d" in options
    tp = Teleplot()
    ts = time.time()  # default to receive time
    for s in samples:
        if s["sensor"] == "Metadata":
            continue
        if s["sensor"] == "BluetoothMetadata":
            bleMeta[s["id"]] = s
            continue

        if s["sensor"].startswith("bluetooth-"):
            if "values_name" in s:
                # variable = key.removeprefix("values_")
                s["name"] = s["values_name"].replace(" ", "_")
                s.pop("values_name")

            elif "id" in s:
                if s["id"] in bleMeta:
                    s["name"] = bleMeta[s["id"]]["name"]
                elif "bluetooth-" + s["id"] in bleMeta:
                    s["name"] = bleMeta["bluetooth-" + s["id"]]["name"]
            sensor = s.get("name", s["sensor"])
        else:
            sensor = s["sensor"]
        for key, value in s.items():
            if key == "name":
                continue
            if key == "sensor":
                continue
            if key == "time":
                ts = float(s["time"]) * 1.0e-9
                continue
            if key in skipKeys:
                continue
            v = make_numeric(value)
            if v:
                variable = key.removeprefix("values_")
                if ts > 1:  # suppress spurious zero timestamps
                    tp.addSample(f"{sensor}.{variable}", v, timestamp=ts)
                continue
            if sensor == "annotation":
                tp.annotate(v, start=ts)
    return tp


def decode(input, options, destfmt, timestamp, debug=False, customDecoder=None):
    j = json.loads(input.decode("utf-8"))
    if "teleplot" in destfmt:
        options = ["decode_ble", "flatten_json"] #+ "gen3d" if "gen3d" in options else []

    if "gpx" in destfmt:
        xml = gengpx.gengpx(j)
        buffer = io.BytesIO()
        buffer.write(xml)
        buffer.seek(0)
        return (".gpx", buffer)

    if "decode_ble" in options:
        decode_ble_beacons(j, debug=debug, customDecoder=customDecoder)
    if "flatten_json" in options:
        result = []
        for report in j:
            result.append(flatten(report))
        j = result

    if "teleplot" in destfmt:
        tp = teleplotify(j, options)
        buffer = io.BytesIO()
        buffer.write(tp.toJson().encode("utf-8"))
        buffer.seek(0)
        return ("-teleplot.json", buffer)

    massaged = traverse_and_modify(
        j, options=options, useless=useless, timestamp=timestamp, debug=debug
    )

    # delete empty dicts
    final = [x for x in massaged if x != {}]

    if "ndjson" in options:
        output = ndjson.dumps(final).encode("utf-8")
    else:
        kwargs = {}
        if "prettyprint" in options:
            kwargs["indent"] = 2
        output = json.dumps(final, **kwargs).encode("utf-8")

    buffer = io.BytesIO()
    buffer.write(output)
    buffer.seek(0)
    return (".json", buffer)


def massage(fa):
    if isinstance(fa, list):  # unfixed
        fl = []
        for fc in fa:
            features = fc["features"]
            cl = []
            for f in features:
                cl.append(f["geometry"]["coordinates"])
            lsf = geojson.Feature(
                geometry=geojson.LineString(cl, properties=fc["description"]),
                properties=fc["description"],
            )
            fl = fl + features + [lsf]
        return geojson.FeatureCollection(features=fl)
    else:
        return fa  # assume fixed


@app.route("/")
def index():
    return redirect("/sensorlogger")
    # return render_template("index.html")


# receive a JSON file by upload
# convert as per options
@app.route("/sensorlogger", methods=["GET", "POST"])
def sensorlogger():
    if request.method == "GET":
        return render_template("sensorlogger.html")
    if request.method == "POST":
        options = request.form.getlist("options")
        destfmt = request.form.getlist("destfmt")
        timestamp = request.form.getlist("timestamp")
        files = request.files.getlist("files")
        for file in files:
            fn = secure_filename(file.filename)
            if fn and allowed_file(fn):
                input = file.stream.read()
                # input = file.stream._file.getvalue()
                (ext, output) = decode(
                    input, options, destfmt, timestamp, customDecoder=custom.Decoder
                )
                base, oldext = os.path.splitext(fn)
                response = make_response(
                    send_file(
                        output,
                        download_name=base + suffix + ext,
                        as_attachment=True,
                    )
                )
                return response


@app.route("/livetrack", methods=["GET", "POST"])
def livetrack():
    if request.method == "GET":
        return render_template("livetrack.html")
    if request.method == "POST":
        app.logger.info(f"rh: {request.headers=}")
        return render_template("qrconfig.html", config="blahfasel")


# push from mobile
@app.route("/tracking", methods=["POST"])
def tracking():
    ah = request.headers.get("Authorization", None)

    app.logger.info(f"livetrack post {ah=} {request.data=}")
    return {}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
