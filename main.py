#!/bin/python3

import time
import subprocess

import paho.mqtt.client as mqtt
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_set_message(client, userdata, msg: mqtt.MQTTMessage):
    cmd = msg.topic.split("/").pop()
    data = str(msg.payload)

    res = subprocess.run(["vclient", "-c", f"'set{cmd} {data}"])
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("mqtt", 1883, 60)

client.subscribe("vito/set/+")
client.message_callback_add("vito/set/+", on_set_message)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

while True:
    res = subprocess.run(["vclient", "-f", "commands", "-j"], capture_output=True, text=True)
    for cmd, val in json.loads(res.stdout).items():
        client.publish("vito/get/" + cmd, val)
    time.sleep(60)
