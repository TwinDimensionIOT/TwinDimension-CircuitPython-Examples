# SPDX-FileCopyrightText: 2023 Luis Pichio, for TwinDimension
# SPDX-License-Identifier: MIT
import time
import board
from digitalio import DigitalInOut
import microcontroller
import gc
#import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from tdata.tdata import TData_MQTT

### WiFi ###

# Add a secrets.py to your filesystem that has a dictionary called secrets with "ssid" and
# "password" keys with your WiFi credentials. DO NOT share that file or commit it into Git or other
# source control.
# pylint: disable=no-name-in-module,wrong-import-order
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])

# Define callback functions which will be called when certain events happen.
# pylint: disable=unused-argument
def connected(client):
    # Connected function will be called when the client is connected to TDATA.
    print("Connected to T>DATA!")

def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new topic.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(client, userdata, topic, pid):
    # This method is called when the client unsubscribes from a topic.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))

# pylint: disable=unused-argument
def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print("Disconnected from TDATA!")

# pylint: disable=unused-argument
def message(client, topic, payload):
    # Message function will be called when a subscribed topic has a new value.
    print("Message received from {0} with value: {1}".format(topic, payload))

def rpc(client, rpc_id, method, params):
    # Message function will be called when a RPC received for a device.
    print("RPC received | rpc_id {0} | method {1} | params {2}".format(rpc_id, method, params))
    client.rpc_response(rpc_id, { "success": True })
    
led1 = DigitalInOut(board.IO41)
led1.switch_to_output()

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="tdata.tesacom.net",
    port=1883,
    username=secrets["tdata_device_token"],
    password="",
    socket_pool=pool,
    #    ssl_context=ssl.create_default_context(),
)

# Initialize an TData Client
tdata_device = TData_MQTT(mqtt_client)

# Connect the callback methods defined above to TDATA
tdata_device.on_connect = connected
tdata_device.on_disconnect = disconnected
tdata_device.on_subscribe = subscribe
tdata_device.on_unsubscribe = unsubscribe
tdata_device.on_message = message
tdata_device.on_rpc = rpc

# Connect to TDATA
print("Connecting to TDATA...")
tdata_device.connect()

device_name = "EP(%02X:%02X:%02X:%02X:%02X:%02X)" % tuple(wifi.radio.mac_address)

print("Subscribe to rpc's")
tdata_device.subscribe_to_rpcs()

lastTelemetry = 0
lastAttributes = 0
print("Publishing telemetry every 10 seconds and attributes every 60...")
while True:
    # Explicitly pump the message loop.
    tdata_device.loop()
    # Send a new message every 10 seconds.
    if (time.monotonic() - lastTelemetry) >= 10:
        lastTelemetry = time.monotonic()
        led1.value = True
        telemetry = {
            "cpu.temperature": microcontroller.cpu.temperature,
            "cpu.voltage": microcontroller.cpu.voltage,
            "gc.mem_alloc": gc.mem_alloc(),
            "gc.mem_free": gc.mem_free(),
            "wifi.radio.ap_info.rssi": wifi.radio.ap_info.rssi,
        }
        print("Publishing telemetry: ", telemetry)
        tdata_device.publish("telemetry", telemetry)

    if (time.monotonic() - lastAttributes) >= 60:
        lastAttributes = time.monotonic()
        led1.value = True
        attributes = {
            "radio.ipv4_address": wifi.radio.ipv4_address,
            "cpu.reset_reason": microcontroller.cpu.reset_reason,
            "cpu.frequency": microcontroller.cpu.frequency,
            "wifi.radio.ap_info.channel": wifi.radio.ap_info.channel,
            "wifi.radio.ap_info.ssid": wifi.radio.ap_info.ssid,
        }
        print("Publishing attributes: ", attributes)
        tdata_device.publish("attributes", attributes)

    if (led1.value):
        led1.value = False
