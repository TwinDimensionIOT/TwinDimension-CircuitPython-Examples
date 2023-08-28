#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a Modbus RTU host (master) which requests or sets data on a client
device.

The RTU communication pins can be choosen freely (check MicroPython device/
port specific limitations).
The register definitions of the client as well as its connection settings like
bus address and UART communication speed can be defined by the user.
"""

# system packages
import time

# import modbus host classes
import board
from digitalio import DigitalInOut
import microcontroller
import gc
from umodbus.serial import Serial as ModbusRTUMaster

import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from tdata.tdata import TData_MQTT_Gateway

# ===============================================
# RTU Master setup
# act as host, collect Modbus data via RTU from a client device
# ModbusRTU can perform serial requests to a client device to get/set data
# check MicroPython UART documentation
# https://docs.micropython.org/en/latest/library/machine.UART.html
# for Device/Port specific setup
#
# RP2 needs "rtu_pins = (Pin(4), Pin(5))" whereas ESP32 can use any pin
# the following example is for an ESP32
# For further details check the latest MicroPython Modbus RTU documentation
# example https://micropython-modbus.readthedocs.io/en/latest/EXAMPLES.html#rtu
tx_pin=board.IO13       # tx pin
rx_pin=board.IO48       # rx pin
de_not_re_pin=board.IO14     # control DE/RE
slave_addr=100
baudrate=9600
led1 = DigitalInOut(board.IO41)
led1.switch_to_output()

print('Using pins {} {} with UART ID {}'.format(tx_pin, rx_pin, slave_addr))

host = ModbusRTUMaster(
    tx_pin=tx_pin,      # tx pin
    rx_pin=rx_pin,      # rx pin
    baudrate=baudrate,  # optional, default 9600
    # data_bits=8,      # optional, default 8
    # stop_bits=1,      # optional, default 1
    # parity=None,      # optional, default None
    de_not_re_pin=de_not_re_pin,  # optional, control DE/RE
    re_de_delay=None,   # optional, re to de delay (us)
    de_re_delay=None   # optional, de to re delay (us)
)

# commond slave register setup, to be used with the Master example above
register_definitions = {
    "HREGS": {
        "HREGS_INTERNALS": {
            "register": 0,
            "len": 50,
        }
    },
}

"""
# alternatively the register definitions can also be loaded from a JSON file
import json

with open('registers/example.json', 'r') as file:
    register_definitions = json.load(file)
"""

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


def message(client, feed_id, payload):
    # Message function will be called when a subscribed topic has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print("Feed {0} received new value: {1}".format(feed_id, payload))


# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="tdata.tesacom.net",
    port=1883,
    username=secrets["tdata_gateway_token"],
    password="",
    socket_pool=pool,
    #    ssl_context=ssl.create_default_context(),
)

# Initialize an TData Client
tdata = TData_MQTT_Gateway(mqtt_client)

# Connect the callback methods defined above to TDATA
tdata.on_connect = connected
tdata.on_disconnect = disconnected
tdata.on_subscribe = subscribe
tdata.on_unsubscribe = unsubscribe
tdata.on_message = message

# Connect to TDATA
print("Connecting to TDATA...")
tdata.connect()

device_name = "EP(%02X:%02X:%02X:%02X:%02X:%02X)" % tuple(wifi.radio.mac_address)

# Below is an example of manually publishing a new  value to TDATA.
lastTelemetry = 0
lastPoll = 0
lastAttributes = 0
lastLedToggle = 0
print("Request & publishing telemetry every 10 seconds and attributes every 60...")
while True:
    now = time.monotonic()
    try:
        # Explicitly pump the message loop.
        tdata.loop()
            
        if now - lastPoll >= 1:
            lastPoll = now
            led1.value = True
            # read holding registers from slave
            print('Requesting and updating data on RTU client at address {} with {} baud'.format(slave_addr, baudrate))
            hreg_address = register_definitions['HREGS']['HREGS_INTERNALS']['register']
            register_qty = register_definitions['HREGS']['HREGS_INTERNALS']['len']
            register_value = host.read_holding_registers(
                slave_addr=slave_addr,
                starting_addr=hreg_address,
                register_qty=register_qty,
                signed=False)
            print('Status of HREG {}: {}'.format(hreg_address, register_value))

        # Send a new message every 10 seconds.
        if now - lastTelemetry >= 10:
            lastTelemetry = now
            led1.value = True
            # prepare & send telemetry
            telemetry = {
                device_name: [
                    {
                        "cpu.temperature": microcontroller.cpu.temperature,
                        "cpu.voltage": microcontroller.cpu.voltage,
                        "gc.mem_alloc": gc.mem_alloc(),
                        "gc.mem_free": gc.mem_free(),
                        "wifi.radio.ap_info.rssi": wifi.radio.ap_info.rssi,                        

                        "slave.cpu.temperature": register_value[0] / 10,
                        "slave.gc.mem_alloc": register_value[1] / 1024.0,
                        "slave.gc.mem_free": register_value[2] / 1024.0,
                    }
                ]
            }
            print("Publishing telemetry: ", telemetry)
            tdata.publish("telemetry", telemetry)

        if now - lastAttributes >= 60:
            lastAttributes = time.monotonic()
            led1.value = True
            attributes = {
                device_name: {
                    "radio.ipv4_address": wifi.radio.ipv4_address,
                    "cpu.reset_reason": microcontroller.cpu.reset_reason,
                    "cpu.frequency": microcontroller.cpu.frequency,
                    "wifi.radio.ap_info.channel": wifi.radio.ap_info.channel,
                    "wifi.radio.ap_info.ssid": wifi.radio.ap_info.ssid,
                }
            }
            print("Publishing attributes: ", attributes)
            tdata.publish("attributes", attributes)
        
        if (led1.value):
            led1.value = False       
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping RTU client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))
        
print("Finished requesting/setting data on client")
