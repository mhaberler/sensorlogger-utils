# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, url_for, render_template, make_response, abort
import loggGps
from TheengsDecoder import decodeBLE
import json

# Directory where we write (and read!) our geojson-data
# dataDir = '/home/<yourPAusername>/fanekart/gpsdata/'
dataDir = "/Users/mah/Ballon/src/sensorlogger-utils/fanekart/gpsdata/"


mySecretGpsKeys = ["uniqueAndSecret123", "topsecret"]


app = Flask(__name__)
app.secret_key = "This is really unique and secret"


@app.route("/")
def hello_world():
    return "Hello from Flask!"


@app.route("/webmap/<filename>")
def map(filename):
    filename = dataDir + filename
    return render_template("webmap.html", config="blahfasel")

    return "Hello from Flask!"


# http://172.16.0.212:5010/getfile/gpsid_kurve.geojson
# app  http://172.16.0.212:5010/fanekart/webmap/index.html
@app.route("/getfile/<filename>")
def getFile(filename):
    filename = dataDir + filename
    try:
        with open(filename) as file:
            blob = file.read()
    except:
        abort(404)

    r = make_response(blob)
    r.mimetype = "application/json"
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r


# fanekart/gpsdata/gpsid_kurve.geojson
# http://172.16.0.212:5010/gpspos/gpsid/dakey/
# b'{"messageId":7,"sessionId":"3fbb1ddc-a645-463b-891e-aa0f4c7c0e97","deviceId":"072aaf1a-c294-4b47-86cd-f97fed7e4f26","payload":[{"name":"bluetooth-e691df7be54d","time":1690393567924000000,"values":{"rssi":-78,"id":"E6:91:DF:7B:E5:4D","txPowerLevel":null,"manufacturerData":"9904050dc5887ca4d901bcfd20024894967a56d4e691df7be54d"}},{"values":{"bearingAccuracy":0,"verticalAccuracy":1.417931318283081,"horizontalAccuracy":20,"speedAccuracy":0,"speed":0.012091556563973427,"bearing":0,"altitude":869,"longitude":15.2118591,"latitude":47.1292252},"name":"location","time":1690393568740000000},{"name":"bluetooth-e691df7be54d","time":1690393570516000000,"values":{"rssi":-77,"id":"E6:91:DF:7B:E5:4D","txPowerLevel":null,"manufacturerData":"9904050dc38885a4d901c0fd20024094967a56d5e691df7be54d"}},{"name":"bluetooth-e691df7be54d","time":1690393571788000000,"values":{"rssi":-77,"id":"E6:91:DF:7B:E5:4D","txPowerLevel":null,"manufacturerData":"9904050dc38885a4d901c0fd20024094967a56d5e691df7be54d"}},{"values":{"bearingAccuracy":0,"verticalAccuracy":1.417931318283081,"horizontalAccuracy":20,"speedAccuracy":0,"speed":0.0026552374474704266,"bearing":0,"altitude":869,"longitude":15.2118591,"latitude":47.1292252},"name":"location","time":1690393572879000000},{"name":"bluetooth-e691df7be54d","time":1690393573069000000,"values":{"rssi":-77,"id":"E6:91:DF:7B:E5:4D","txPowerLevel":null,"manufacturerData":"9904050dc38882a4d901bcfd28024494967a56d6e691df7be54d"}},{"values":{"bearingAccuracy":0,"verticalAccuracy":1.3752892017364502,"horizontalAccuracy":20,"speedAccuracy":0,"speed":0.012174158357083797,"bearing":0,"altitude":869,"longitude":15.2118581,"latitude":47.1292252},"name":"location","time":1690393578752000000},{"values":{"bearingAccuracy":0,"verticalAccuracy":1.3752892017364502,"horizontalAccuracy":20,"speedAccuracy":0,"speed":0.0029675213154405355,"bearing":0,"altitude":869,"longitude":15.211858,"latitude":47.1292252},"name":"location","time":1690393582895000000}]}'
@app.route("/gpspos/<gpsId>/<secretGpsKey>/", methods=["GET", "POST"])
def getpos(gpsId="", secretGpsKey=""):
    # if secretGpsKey not in mySecretGpsKeys:
    #     abort(401)
    #     pass
    body = json.loads(request.data)
    messageId = body["messageId"]
    sessionId = body["sessionId"]
    deviceId = body["deviceId"]
    for p in body["payload"]:
        if p.get("name", None) == "location":
            time = p["time"]
            lat = p["values"]["latitude"]
            lon = p["values"]["longitude"]
            alt = p["values"]["altitude"]
            app.logger.info(f"post {lat=} {lon=} {alt=}")
            ok = loggGps.loggGps(str(lat), str(lon), str(gpsId), dataDir)
    return {}
