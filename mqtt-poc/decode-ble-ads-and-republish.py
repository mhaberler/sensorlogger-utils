import os
import json
import shortuuid
import paho.mqtt.client as mqtt
from TheengsDecoder import decodeBLE 
from TheengsDecoder import getProperties, getAttribute

def on_connect(mqttc, obj, flags, rc):
    print("rc: "+str(rc))

def on_message(mqttc, obj, msg):
    e = msg.topic.split("/")
    slclient = e[2]
    bledev = e[5]
    data_json = decodeBLE(msg.payload.decode())
    
    if data_json:
        # successfully decoded, republish:
        mqttc.publish(f"/sensorlogger/{slclient}/ble/values/{bledev}", json.dumps(data_json))        
        print(f"{slclient} {bledev} {data_json}")
            


mqttc = mqtt.Client(f'client-{shortuuid.uuid()}', transport="websockets")
mqttc.ws_set_options(path="/mqtt", headers=None)
mqttc.tls_set()
mqttc.username_pw_set(username=os.getenv("MQTT_USER"),password=os.getenv("MQTT_PASS"))
mqttc.on_message = on_message
mqttc.on_connect = on_connect


print(f'trying to connect.....')
mqttc.connect(os.getenv("MQTT_BROKER"), 443, 60)

mqttc.subscribe("/sensorlogger/+/ble/ads/+", 0)

mqttc.loop_forever()
