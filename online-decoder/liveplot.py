from flask import render_template, request, current_app, Blueprint

from flask_socketio import SocketIO, Namespace
from threading import Lock
import json
import shortuuid
import socket, queue
import time
import os
from TheengsDecoder import decodeBLE
from flatten_json import flatten
import custom
from slconfig import merge, gen_export_code
from bleads import decode_advertisement

# from operator import itemgetter
# from collections import defaultdict

liveplot = Blueprint("liveplot", __name__, template_folder="templates")

UDP_IP = "0.0.0.0"
UDP_PORT = 0  #  choose ephemeral port
SESSION_MAX_AGE = 3600 * 24
state = "sessions.json"

sessions = {}
namespaces = {}
queues = {}
sl_threads = {}
udp_threads = {}
bleMeta = {}
udp_thread_lock = Lock()
sl_thread_lock = Lock()

app = None
socketio = None


def open_udp_port(ip="0.0.0.0", portno=0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, portno))
    addr, port = s.getsockname()
    app.logger.info(f"udp getsockname({addr}, {port})")
    return s, addr, port


def udp_job(app, s, namespace):
    with app.app_context():
        startup = time.time()
        app.logger.info(f"udp_job for {namespace.namespace} started")
        while True:
            data, _ = s.recvfrom(4096)
            msg = {
                "data": data.decode(),
                "timestamp": time.time(),
            }
            namespace.emit("udp", msg)
            if startup + SESSION_MAX_AGE < time.time():
                break
        app.logger.info(f"udp_job for {namespace.namespace} ended")


def sl_job(app, q, namespace):
    with app.app_context():
        app.logger.info(f"sl_job for {namespace.namespace} started")
        startup = time.time()
        while True:
            msg = q.get()
            channel = msg.get("channel", "udp")
            namespace.emit(channel, msg)
            if startup + SESSION_MAX_AGE < time.time():
                break
        app.logger.info(f"sl_job for {namespace.namespace} ended")


class TeleplotNamespace(Namespace):
    def on_connect(self):
        app.logger.info(f"{self.namespace=} on_connect")
        # emit("slconnect")

    def on_disconnect(self):
        app.logger.info(f"{self.namespace=} on_disconnect")

    def on_message(self, m):
        pass
        # app.logger.info(f"{self.namespace=} on_message {m}")

    def on_error(self):
        app.logger.info(f"{self.namespace=} on_error")

    def on_tpconnect(self, data):
        app.logger.info(f"{self.namespace=} tpconnect received {data=}")
        # emit("slconnect", data)

    def on_json(self, data):
        app.logger.info(f"{self.namespace=} on_json received {data=}")


def decode_ble_beacons(j, debug=False, customDecoder=None):
    global bleMeta
    result = []
    for sample in j:
        try:
            adv = sample["values"]["advertisement"]
            da = decode_advertisement(adv)
            if "SVC_DATA_UUID16" in da:
                sample["values"]["servicedata"] = da['SVC_DATA_UUID16'][2:].hex()
                # app.logger.info(f"servicedata= '{da['SVC_DATA_UUID16'][2:].hex()} {adv=}'")
                # sample["values"].update(da)
        except KeyError:
            pass
        if sample["name"].startswith("bluetoothmetadata"):
            # app.logger.info(f"bluetoothmetadata: '{sample}'")

            ssuids = sample["values"].get("serviceUUIDs", [])
            if not isinstance(ssuids, list):
                # mutate so we always have a list of serviceUUIDs
                sample["values"]["serviceUUIDs"] = [ssuids]
            id = sample["values"]["id"]
            sid = "bluetooth-" + id.replace(":", "").lower()
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
            try:
                #data["servicedata"] =  "0224b2070113100c08fdff4a0b" 
                data["servicedata"] = sample["values"]["servicedata"]
                # app.logger.info(f"ADDED: '{data['servicedata']}'")

            except KeyError:
                pass
            data["id"] = sample["values"]["id"]
            data["time"] = sample["time"]
            data["rssi"] = sample["values"]["rssi"]
            data["manufacturerdata"] = sample["values"]["manufacturerData"]
            input = json.dumps(data)
            # app.logger.info(f"data sent to decoder: '{input}'")
            # input = '{"servicedatauuid": "181b", "servicedata": "0224b2070113100c08fdff4a0b", "manufacturerdata": "5701381ec781c63c", "name": "MIBFS", "id": "5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28", "rssi": -67}'
            # input = '{"servicedatauuid": "181b", "manufacturerdata": "5701381ec781c63c", "name": "MIBFS", "id": "5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28", "rssi": -67}'
            # {"name": "MIBFS", "servicedatauuid": "181b", "id": "2b79964c-23a6-aba8-ed42-b4351592548d", "time": 1691300324099000000, "rssi": -73, "manufacturerdata": "5701381ec781c63c"}'

            #data sent to decoder:  {"servicedatauuid": "181b", "servicedata": "0224b207011e042522fdffcc0b", "manufacturerdata": "5701381ec781c63c", "name": "MIBFS", "id": "5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28", "rssi": -67}

            #OK data sent to decoder:  {"servicedatauuid": "181b", "servicedata": "0224b207011e042522fdffcc0b", "manufacturerdata": "5701381ec781c63c", "name": "MIBFS", "id": "5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28", "rssi": -67}
            #NOKdata sent to decoder: '{"name": "MIBFS", "servicedatauuid": "181b", "servicedata": "0204b207011e041b0d0000f807", "id": "38:1E:C7:81:C6:3C", "time": 1692208603262000000, "rssi": -65, "manufacturerdata": "5701381ec781c63c"}'
            #OK TheengsDecoder found device: {"servicedatauuid":"181b","servicedata":"0224b207011e042522fdffcc0b","manufacturerdata":"5701381ec781c63c","name":"MIBFS","id":"5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28","rssi":-67,"brand":"Xiaomi","model":"Mi Body Composition Scale","model_id":"XMTZC02HM/XMTZC05HM","type":"SCALE","weighing_mode":"person","unit":"kg","weight":15.1}


            # "0204b207011e041b0d0000f807"
            # "0224b207011e042522fdffcc0b"
            ret = decodeBLE(input)
            #   data sent to decoder:  {"servicedatauuid": "181b", "servicedata": "0224b2070113100c08fdff4a0b", "manufacturerdata": "5701381ec781c63c", "name": "MIBFS", "id": "5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28", "rssi": -67}
            # TheengsDecoder found device: {"servicedatauuid":"181b","servicedata":"0224b2070113100c08fdff4a0b","manufacturerdata":"5701381ec781c63c","name":"MIBFS","id":"5732A8DA-27AF-1C19-DA77-C8EF5AD5CB28","rssi":-67,"brand":"Xiaomi","model":"Mi Body Composition Scale","model_id":"XMTZC02HM/XMTZC05HM","type":"SCALE","weighing_mode":"person","unit":"kg","weight":14.45}
            if ret:
                js = json.loads(ret)
                js.pop("id", None)
                js.pop("mfid", None)
                js.pop("manufacturerdata", None)
                js.pop("servicedatauuid", None)
                js.pop("servicedata", None)
                # app.logger.info(f"decodeBLE: '{js}'")
                result.append(js)
                continue

            if customDecoder:
                ret = customDecoder(data, debug)
                if ret:
                    # app.logger.info(f"customDecoder: '{ret}'")
                    sample["name"] = data["name"]
                    sample["values"] = ret
                    result.append(sample)
                    continue
        result.append(sample)
    return result


# myValue:1627551892444:1;1627551892555:2;1627551892666:3

# https://stackoverflow.com/questions/50505381/python-split-a-list-of-objects-into-sublists-based-on-objects-attributes


def teleplotify(samples, clientsession):
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
                ts = s["time"] * 1.0e-6
                continue
            if isinstance(value, float) or isinstance(value, int):
                variable = key.removeprefix("values_")
                if isinstance(value, bool):
                    value = int(value)
                tp = {
                    "data": f"{sensor}.{variable}:{ts}:{value}|np\n",
                }
                if ts > 1:  # suppress spurious zero timestamps
                    queues[clientsession].put(tp)
                continue
            if sensor == "annotation":
                queues[clientsession].put(
                    {
                        "channel": "json",
                        "data": {"annotation": {"label": value, "from": ts * 1e-3}},
                        "timestamp": time.time(),
                    }
                )


@liveplot.route("/sl/<clientsession>", methods=["POST"])
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

    age = int(time.time() - sessions[clientsession]["lastUse"])
    if age > SESSION_MAX_AGE:
        return f"Session timed out - link age is {age} seconds", 404

    # check for test push
    for p in payload:
        if p.get("name", None) == "test":
            app.logger.info(
                f"client test push: {clientsession=} {messageId=} {sessionId=} {deviceId=}"
            )
            namespaces[clientsession].emit(
                "udp",
                {
                    "data": f">:test push : {clientsession=} {messageId=} {sessionId=} {deviceId=}\n",
                },
            )
            return {}

    if not "deviceId" in sessions[clientsession]:
        sessions[clientsession]["deviceId"] = deviceId

    if not clientsession in queues:
        app.logger.info(f"no queue for {clientsession}")
        return {}

    # record last messageId
    sessions[clientsession]["messageId"] = messageId
    # refresh expiration timer
    sessions[clientsession]["lastUse"] = time.time()

    # app.logger.info(
    #             f"post: {body=}"
    #         )
    result = decode_ble_beacons(payload, debug=False, customDecoder=custom.Decoder)
    flattened = []
    for report in result:
        flattened.append(flatten(report))
    teleplotify(flattened, clientsession)
    return {}


@liveplot.route("/plot", methods=["GET", "POST"])
def plot():
    app.logger.info(f"plot {request.method=}")
    if request.method == "GET":
        return render_template("plot.html")
    if request.method == "POST":
        sessionKey = shortuuid.uuid()
        authToken = shortuuid.uuid()
        url = request.host_url + "sl/" + sessionKey
        sessions[sessionKey] = {
            "authToken": authToken,
            "lastUse": time.time(),
            "url": url,
        }
        tpns = TeleplotNamespace("/" + sessionKey)
        socketio.on_namespace(tpns)
        namespaces[sessionKey] = tpns
        queues[sessionKey] = queue.Queue()

        # sensorlogger-to-teleplot bridging thread
        with sl_thread_lock:
            if not sessionKey in sl_threads:  # once only
                sl_threads[sessionKey] = socketio.start_background_task(
                    sl_job,
                    current_app._get_current_object(),
                    queues[sessionKey],
                    namespaces[sessionKey],
                )

        # udp-to-teleplot bridging thread
        with udp_thread_lock:
            if not sessionKey in udp_threads:  # once only
                s, _, port = open_udp_port(ip=UDP_IP, portno=UDP_PORT)
                sessions[sessionKey]["udp_port"] = port
                udp_threads[sessionKey] = socketio.start_background_task(
                    udp_job,
                    current_app._get_current_object(),
                    s,
                    namespaces[sessionKey],
                )

        params = {
            "http": {
                "enabled": True,
                "url": url,
                "authToken": "Bearer " + authToken,
            },
        }
        cfg = merge(request, params)
        sessions[sessionKey]["config_code"] = cfg
        with open(state, "w") as f:
            f.write(json.dumps(sessions, indent=4))
        app.logger.info(f"{len(sessions.keys())} sessions saved")
        configCode = len(request.form.getlist("configCode")) > 0

        return render_template(
            "genqrcode.html",
            config=json.dumps(cfg, indent=2) if configCode else "",
            cchdr="QRcode contents:" if configCode else "",
            config_img=gen_export_code(cfg),
            clientsession=sessionKey,
            udp_port=sessions[sessionKey]["udp_port"],
            tppath="/tp",
        )
    return {}


@liveplot.route("/tp")
def teleplot():
    s = request.args.get("session")
    app.logger.info(f"/tp: session={s}")
    return render_template("teleplot.html", clientsession=s)


def init_liveplot(a):
    global socketio
    global app
    app = a
    socketio = SocketIO(async_mode="threading")
    socketio.init_app(a)


def restore_sessions(app):
    if os.path.exists(state):
        with open(state) as f:
            sessions = json.loads(f.read())
        app.logger.info(f"{len(sessions.keys())} sessions loaded")
        expired = []
        for sessionKey in sessions.keys():
            age = time.time() - sessions[sessionKey]["lastUse"]
            if age > SESSION_MAX_AGE:
                app.logger.info(f"expiring session {sessionKey} - age {age/3600} hours")
                expired.append(sessionKey)
                continue
            tpns = TeleplotNamespace("/" + sessionKey)
            socketio.on_namespace(tpns)
            namespaces[sessionKey] = tpns
            queues[sessionKey] = queue.Queue()
            # sensorlogger-to-teleplot bridging thread
            with app.app_context():
                with sl_thread_lock:
                    if not sessionKey in sl_threads:  # once only
                        sl_threads[sessionKey] = socketio.start_background_task(
                            sl_job,
                            current_app._get_current_object(),
                            queues[sessionKey],
                            namespaces[sessionKey],
                        )

                # udp-to-teleplot bridging thread
                with udp_thread_lock:
                    if not sessionKey in udp_threads:  # once only
                        s, _, port = open_udp_port(ip=UDP_IP, portno=UDP_PORT)
                        sessions[sessionKey]["udp_port"] = port
                        udp_threads[sessionKey] = socketio.start_background_task(
                            udp_job,
                            current_app._get_current_object(),
                            s,
                            namespaces[sessionKey],
                        )
        for k in expired:
            sessions.pop(k)
