class ConnectionTeleplotWebsocket extends Connection {
    constructor() {
        super();
        this.name = ""
        this.type = "teleplot-websocket";
        this.inputs = [];
        this.socket = null;
        this.address = "";
        this.port = "";
        this.udp = new DataInputUDP(this, "UDP");
        this.udp.address = "";
        this.udp.port = UDPport;
        this.supportSerial = true;
        this.inputs.push(this.udp);
    }

    connect(_address, _port) {
        this.name = _address + ":" + _port;
        this.address = _address;
        this.port = _port;
        this.udp.address = this.address;
        const uri = "ws://" + this.address + ":" + this.port; //  + "/tpws";
        // this.socket = new WebSocket(uri);
        this.socket = new io(uri);
        this.socket.udp = this.udp;
        this.socket.connect();
        this.socket.onopen = (event) => {
            this.udp.connected = true;
            this.connected = true;
            this.sendServerCommand({ cmd: "listSerialPorts" });
        };
        this.socket.onclose = (event) => {
            this.udp.connected = false;
            this.connected = false;
            for (let input of this.inputs) {
                input.disconnect();
            }
            setTimeout(() => {
                this.connect(this.address, this.port);
            }, 2000);
        };
        this.socket.on("sl", function (data) {
            // let msg = JSON.parse(data);
            console.log("sl", data);
        });
        // {
        //     "data": "\nmyValue:1234\n",
        //     "fromSerial": false,
        //     "timestamp": 1690971162263
        // }
        this.socket.on("udp", function (msg) {
            // let msg = JSON.parse(data);
            console.log("udp", msg);
            if ("id" in msg) {
                for (let input of this.inputs) {
                    if (input.id == msg.id) {
                        input.onMessage(msg);
                        break;
                    }
                }
            }
            else {
                this.udp.onMessage(msg);
            }
        });
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