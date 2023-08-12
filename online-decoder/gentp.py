import json
import time


class Telemetry:
    def __init__(self, name, type="number", precision=4) -> None:
        self.name = name
        self.type = type
        self.values = []
        self.timestamps = []
        self.usageCount = 0
        self.precision = precision

    def addSample(self, value, timestamp=time.time()):
        self.values.append(value)
        self.timestamps.append(timestamp)

    def generate(self):
        return {
            "type": self.type,
            "name": self.name,
            "usageCount": self.usageCount,
            "values": [self.values[-1]],
            "data": [self.timestamps, self.values],
            "pendingData": [[], []],
            "values_formatted": f"{self.values[-1]:.{self.precision}f}",
        }


class Teleplot:
    def __init__(self) -> None:
        self.telemetries = {}
        self.logs = []
        self.annotations = []

    def addSample(self, name, value, timestamp=time.time(), type="number",precision=4):
        if not name in self.telemetries:
            self.telemetries[name] = Telemetry(name, type=type, precision=precision)
        self.telemetries[name].addSample(value, timestamp=timestamp)

    def annotate(self, label, start=time.time(), end=None):
        self.annotations.append(
            {"label": label, "from": start, "to": end if end else start}
        )

    def toJson(self):
        data = {
            "telemetries": {},
            "logs": [],
            "dataAvailable": True,
            "logAvailable": False,
            "annotations": self.annotations,
        }
        for name in self.telemetries.keys():
            data["telemetries"][name] = self.telemetries[name].generate()
        return json.dumps(data, indent=4)




if __name__ == "__main__":
    from math import sin, cos, pi

    t = time.time()
    tp = Teleplot()

    numpts = 100
    tp.annotate("begin", t + 1)
    tp.annotate("range", t + 20, t + 30)

    for i in range(numpts):
        t += 1
        alpha = 2 * pi * i / numpts
        tp.addSample("sin", sin(alpha), t)
        tp.addSample("cos",cos(alpha), t)
    tp.annotate("end", t - 1)
    with open("test.json", "w") as f:
        f.write(tp.toJson())
