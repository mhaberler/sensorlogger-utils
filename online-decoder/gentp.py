import json
import time

telemetries = {}
logs = []
annotations = []


class Telemetry:
    def __init__(self, name, type="number", precision=4) -> None:
        self.name = name
        self.type = type
        self.values = []
        self.timestamps = []
        self.usageCount = 0
        self.precision = precision
        telemetries[name] = self

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
        
def annotate(label, start=time.time(), end=None):
    annotations.append({
        "label":label,
        "from": start,
        "to" : end if end else start
    })

def save(name):
    with open(name, "w") as f:
        data = {
            "telemetries": {},
            "logs": [],
            "dataAvailable": True,
            "logAvailable": False,
            "annotations": annotations
        }
        for name in telemetries.keys():
            data["telemetries"][name] = telemetries[name].generate()
        f.write(json.dumps(data, indent=4))

if __name__ == "__main__":
    from math import sin,cos,pi
    t = time.time()
    s = Telemetry("sin")
    c = Telemetry("cos")
    numpts = 100
    annotate("begin",t+1)
    annotate("range",t+20,t+30)

    for i in range(numpts):
        t += 1
        alpha = 2*pi*i/numpts
        s.addSample(sin(alpha),t)
        c.addSample(cos(alpha),t)
    annotate("end",t-1)

    save("test.json")