#!/bin/python3

import time
import subprocess

import paho.mqtt.client as mqtt
import json
import re
from threading import RLock

lock = RLock()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    pass

loop_timer = 0
cmds = {}

def on_set_message(client, userdata, msg: mqtt.MQTTMessage):
    cmd = msg.topic.split("/").pop()
    data = str(msg.payload.decode())

    print(msg.topic+" "+str(msg.payload))
    with lock:
        cmds[f"set{cmd} {data}"] = 5

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.2.102", 1883, 60)

client.subscribe("vito/set/+")
client.message_callback_add("vito/set/+", on_set_message)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_start()

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

def get_errors(output: str):
    ret = []
    for line in output.splitlines():
        res = re.match("Error executing (.*)", line)
        if res:
            cmd = res.group(1)
            print("Error: " + cmd)
            cmd = remove_prefix(cmd, "get")
            ret.append(cmd)
    return ret


while True:
    completed = []
    with lock:
        for cmd in cmds.keys():
            print(f"Executing cmd: {cmd}")
            res = subprocess.run(["vclient", "-c", cmd], capture_output=True, text=True)
            errors = get_errors(res.stderr)
            if len(errors) > 0:
                print(res.stderr)
                print(f"Retrying {cmds[cmd]}: {cmd}")
                cmds[cmd] = cmds[cmd] - 1
                if cmds[cmd] == 0:
                    completed.append(cmd)
            else:
                completed.append(cmd)
            loop_timer = 0

    for cmd in completed:
        cmds.pop(cmd)
    if loop_timer == 0:
        print("Reading")
        '''
        try:
            res = subprocess.run(["vclient", "-f", "commands", "-j"], capture_output=True, text=True)
            errors = get_errors(res.stderr)
            for cmd, val in json.loads(res.stdout).items():
                cmd = remove_prefix(cmd, "get")
                if not cmd in errors:
                    client.publish("vito/get/" + cmd, val)
                    #print(f"{cmd}: {val}")
                else:
                    print(f"Discard {cmd}: {val}")
        except:
            pass
            '''
        try:
            res = subprocess.run(["vclient", "-f", "commands", "-J"], capture_output=True, text=True)
            #print(res.stdout.strip().replace("\n", "\\n"))
            errors = get_errors(res.stderr)
            for item in json.loads(res.stdout.strip().replace("\n", "\\n")):
                cmd = remove_prefix(item["command"], "get")
                if not item["error"]:
                    client.publish("vito/getJson/" + cmd, json.dumps(item))
                    client.publish("vito/get/" + cmd, item["value"])
                else:
                    client.publish("vito/getJsonError/" + cmd, json.dumps(item))
        except Exception as e:
            print(e)
            pass
        loop_timer = 60
    else:
        loop_timer = loop_timer - 1
    time.sleep(1)
