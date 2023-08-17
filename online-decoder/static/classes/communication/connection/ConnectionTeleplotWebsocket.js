class ConnectionTeleplotWebsocket extends Connection {
    constructor() {
        super();
        this.name = ""
        this.type = "teleplot-websocket";
        this.inputs = [];
        this.socket = null;
        this.address = "";
        this.port = "";
        this.supportSerial = true;

        this.udp = new DataInputUDP(this, "UDP");
        this.udp.address = "";
        this.udp.port = UDPport;
        this.inputs.push(this.udp);

        // this.sio = new DataInputSocketio(this, "SocketIO");
        // this.inputs.push(this.sio);
    }

    connect(_address, _port) {
        this.name = _address + ":" + _port;
        this.address = _address;
        this.port = _port;
        this.udp.address = this.address;
        const uri = "ws://" + this.address + ":" + this.port + "/tp/" + session;
        this.socket = new WebSocket(uri);
        this.socket.udp = this.udp;
        // this.socket.connect();
        this.socket.onopen = function (ev) {
            this.udp.connected = true;
            this.connected = true;
            this.send(JSON.stringify({ cmd: "listSerialPorts" }));
        };
        this.socket.onclose = function (ev) {
            if (ev.wasClean) {
                console.log(`[close] Connection closed cleanly, code=${ev.code} reason=${ev.reason}`);
            } else {
                // e.g. server process killed or network down
                // event.code is usually 1006 in this case
                console.log(`[close] Connection died code=${ev.code} reason=${ev.reason}`);
            }
            this.udp.connected = false;
            this.connected = false;
            for (let input of this.inputs) {
                input.disconnect();
            }
            // setTimeout(() => {
            //     this.connect(this.address, this.port);
            // }, 2000);
        };
        this.socket.onerror = function (error) {
            console.log(`[error]`);
        };

        this.socket.onmessage = function (ev) {
            const msg = JSON.parse(ev.data);
            if ("json" in msg) {
                msg.input = this;
                parseJson(msg);
            }
            else if ("data" in msg) {
                parseData(msg);
                // this.udp.onMessage(msg);
            }
            else if ("cmd" in msg) {
                //nope
            }
        };
        // this.socket.on("udp", function (msg) {
        //     // console.log("udp", msg);
        //     if ("id" in msg) {
        //         for (let input of this.inputs) {
        //             if (input.id == msg.id) {
        //                 input.onMessage(msg);
        //                 break;
        //             }
        //         }
        //     }
        //     else {
        //         this.udp.onMessage(msg);
        //     }
        // });
        return true;
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    sendServerCommand(command) {
        if (this.socket) this.socket.send(JSON.stringify(command));
    }

    updateCMDList() {
        for (let input of this.inputs) {
            input.updateCMDList();
        }
    }

    createInput(type) {
        if (type == "serial") {
            let serialIn = new DataInputSerial(this, "Serial");
            this.inputs.push(serialIn);
        }
    }
}