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
import geojson
from TheengsDecoder import decodeBLE
from TheengsDecoder import getProperties, getAttribute
import codecs
import custom

# pip install git+https://github.com/mhaberler/uttlv.git@ltv-option

from uttlv import TLV
import bleads

app = Flask(__name__)
app.config.from_object(__name__)
app.config["UPLOAD_FOLDER"] = "/tmp/sensorlogger-upload"

ALLOWED_EXTENSIONS = ["zip", "json"]

reader = codecs.getreader("utf-8")



def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def decode(input, debug=False, customDecoder=None):
    j = json.loads(input.decode("utf-8"))
    bleMeta = {}
    for sample in j:
        if sample["sensor"].startswith("BluetoothMetadata"):
            # iOS example:
            # {
            #     "sensor": "BluetoothMetadata",
            #     "time": "1689983283060000000",
            #     "seconds_elapsed": "0.061",
            #     "id": "659702ad-9718-92af-2443-eaabfe9f494d",
            #     "name": "TPMS1_121A64",
            #     "localName": "",
            #     "isConnectable": "0",
            #     "serviceUUIDs": "fbb0"
            # },
            # android example:
            # {
            #     "sensor": "BluetoothMetadata",
            #     "time": "1689983118942000000",
            #     "seconds_elapsed": "0.103000244140625",
            #     "id": "DC:23:4D:EB:88:46",
            #     "name": "TY",
            #     "localName": "TY",
            #     "isConnectable": "true",
            #     "serviceUUIDs": [
            #     "a201"
            #     ]
            # },
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
                sample["decoded"] = js
                if debug and sample["decoded"]:
                    print(json.dumps(sample, indent=2))
                continue

            if customDecoder:
                result = customDecoder(data, debug)
                if result:
                    sample["decoded"] = result
                    continue
            # try splitting up the advertisement
            tlv = TLV(len_size=1,ltv=True,lenTV=True)
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
                    sample["decoded"] = js
                    if debug and sample["decoded"]:
                        print(json.dumps(sample, indent=2))
                continue

    output = json.dumps(j, indent=2).encode("utf-8")
    buffer = io.BytesIO()
    buffer.write(output)
    buffer.seek(0)
    return buffer


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
    return render_template("index.html")

@app.route("/traj", methods=["POST"])
def traj():
    j = json.loads(request.data)
    f = open('traj-orig.json', 'w')
    f.write(json.dumps(j, indent=4))
    f.close()
    f = open('traj-geojson.json', 'w')
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
            file.save(
                os.path.join(app.config["UPLOAD_FOLDER"], base + "-decoded" + ext)
            )
    return redirect("/")  # change to redirect to your own url


# receive a JSON file by upload
# convert BLE ads
# send JSON file as <basename>-decoded.json
@app.route("/decode_ble", methods=["POST"])
def decode_ble():
    files = request.files.getlist("files")
    for file in files:
        fn = secure_filename(file.filename)
        if fn and allowed_file(fn):
            input = file.stream.read()
            # input = file.stream._file.getvalue()
            output = decode(input, customDecoder=custom.Decoder)
            base, ext = os.path.splitext(fn)
            response = make_response(
                send_file(
                    output, download_name=base + "-decoded" + ext, as_attachment=True
                )
            )
            return response


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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
