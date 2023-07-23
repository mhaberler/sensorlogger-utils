#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from datetime import datetime
from flask import (
    Flask,
    render_template,
    jsonify,
    redirect,
    url_for,
    request,
    make_response,
    send_file,
)
from werkzeug.utils import secure_filename
import io
import zipfile
import json
import ndjson
import geojson
from TheengsDecoder import decodeBLE
from TheengsDecoder import getProperties, getAttribute
import codecs
import custom
from flatten_json import flatten
import arrow
import gengpx

# pip install git+https://github.com/mhaberler/uttlv.git@ltv-option

from uttlv import TLV
import bleads

app = Flask(__name__)
app.config.from_object(__name__)
app.config["UPLOAD_FOLDER"] = "/tmp/sensorlogger-upload"

ALLOWED_EXTENSIONS = ["zip", "json"]

reader = codecs.getreader("utf-8")
decoded = "values"
suffix = "-processed"
metadataNames = ["BluetoothMetadata", "Metadata"]
useless = ["manufacturerData"]


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
                    print(f"drop {key=}")
                obj.pop(key)
                continue
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
            if meta["localName"]:
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
                    print(json.dumps(sample, indent=2))
                continue

            if customDecoder:
                result = customDecoder(data, debug)
                if result:
                    sample[decoded] = result
                    continue
            # try splitting up the advertisement
            tlv = TLV(len_size=1, ltv=True, lenTV=True)
            tlv.set_tag_map(bleads.bleAdvConfig)
            tlv.parse_array(bytes(bytearray.fromhex(data["manufacturerdata"])))
            if bleads.BLE_HS_ADV_TYPE_MFG_DATA in tlv:  # ha!
                data = {}
                if meta["localName"]:
                    data["name"] = meta["localName"]
                sl = meta["serviceUUIDs"][0]
                if len(sl) > 4:
                    sl = sl[4:8]
                data["servicedatauuid"] = sl
                data["id"] = sample["id"]
                data["rssi"] = sample["rssi"]
                data["manufacturerdata"] = tlv[bleads.BLE_HS_ADV_TYPE_MFG_DATA].hex()
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
                        print(json.dumps(sample, indent=2))
                continue
    return


def decode(input, options, destfmt, timestamp, debug=False, customDecoder=None):
    j = json.loads(input.decode("utf-8"))

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

    massaged = traverse_and_modify(
        j, options=options, useless=useless, timestamp=timestamp, debug=debug
    )

    # delete empty dicts
    final = [x for x in massaged if x != {}]
    
    if "ndjson" in options:
        output = ndjson.dumps(final).encode("utf-8")
    else:
        kwargs={}
        if "prettyprint" in options:
            kwargs['indent'] = 2
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
    return redirect('/sensorlogger')
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
                (ext,output) = decode(
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


@app.route("/form", methods=["GET", "POST"])
def form():
    if request.method == "GET":
        return render_template("form.html")
    if request.method == "POST":
        # option = request.form['options']
        if "download" in request.form:
            return {}
        elif "watch" in request.form:
            return {}


@app.route("/traj", methods=["POST"])
def traj():
    j = json.loads(request.data)
    f = open("traj-orig.json", "w")
    f.write(json.dumps(j, indent=4))
    f.close()
    f = open("traj-geojson.json", "w")
    m = massage(j)
    f.write(geojson.dumps(m, indent=4))
    f.close()
    return {}


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    for file in files:
        fn = secure_filename(file.filename)
        if fn and allowed_file(fn):
            base, ext = os.path.splitext(fn)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], base + suffix + ext))
    return redirect("/")  # change to redirect to your own url


# upload several files
# zip them
# return the zip archvive
@app.route("/zip", methods=["POST"])
def zip():
    files = request.files.getlist("files")
    zipped_file = io.BytesIO()
    with zipfile.ZipFile(zipped_file, "w") as zipper:
        for file in files:
            fn = secure_filename(file.filename)
            zipper.writestr(fn, file.stream._file.getvalue())
    zipped_file.seek(0)
    response = make_response(
        send_file(zipped_file, download_name="export.zip", as_attachment=True)
    )
    return response


# upload zip archive
# return list of files in archive
@app.route("/postzip", methods=["POST"])
def postzip():
    file = request.files["data_zip_file"]
    file_like_object = file.stream._file
    zipfile_ob = zipfile.ZipFile(file_like_object)
    file_names = zipfile_ob.namelist()
    # Filter names to only include the filetype that you want:
    # file_names = [file_name for file_name in file_names if file_name.endswith(".txt")]
    # files = [(zipfile_ob.open(name).read(),name) for name in file_names]
    return str(file_names)


# @app.route("/download")
# def download():
#     return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
