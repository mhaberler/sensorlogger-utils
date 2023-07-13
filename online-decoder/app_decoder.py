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
import csv
import zipfile
import json
import geojson
from TheengsDecoder import decodeBLE
from TheengsDecoder import getProperties, getAttribute
import sys
import codecs
import custom

app = Flask(__name__)
app.config.from_object(__name__)
app.config["UPLOAD_FOLDER"] = "/tmp/sensorlogger-upload"

ALLOWED_EXTENSIONS = ["zip", "json"]

reader = codecs.getreader("utf-8")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def decode(input, debug=False, customDecoder=None):
    j = json.loads(input.decode("utf-8"))
    for sample in j:
        if sample["sensor"].startswith("Bluetooth"):
            data = {}
            data["name"] = sample["name"]
            data["id"] = sample["id"]
            try:
                # Kelvin fix needed
                # this should be an array
                # data['servicedatauuid'] = list(sample['serviceUUIDs'])
                data["servicedatauuid"] = [sample["serviceUUIDs"]]
            except KeyError:
                pass
            data["manufacturerdata"] = sample["manufacturerData"]
            result = decodeBLE(json.dumps(data))
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
            input = file.stream._file.getvalue()
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
    app.run(debug=True, port=5001)
