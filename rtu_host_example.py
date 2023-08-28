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
from umodbus.serial import Serial as ModbusRTUMaster

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

print('Using pins {} {} with UART ID {}'.format(tx_pin, rx_pin, slave_addr))

host = ModbusRTUMaster(
    tx_pin=tx_pin,      # tx pin
    rx_pin=rx_pin,      # rx pin
    baudrate=baudrate,  # optional, default 9600
    # data_bits=8,      # optional, default 8
    # stop_bits=1,      # optional, default 1
    # parity=None,      # optional, default None
    de_not_re_pin=de_not_re_pin,  # optional, control DE/RE
    # re_de_delay=200   # optional, re to de delay (us)
    # de_re_delay=100   # optional, de to re delay (us)
)

# commond slave register setup, to be used with the Master example above
register_definitions = {
    "COILS": {
        "RESET_REGISTER_DATA_COIL": {
            "register": 42,
            "len": 1,
            "val": 0
        },
        "EXAMPLE_COIL": {
            "register": 123,
            "len": 1,
            "val": 1
        }
    },
    "HREGS": {
        "EXAMPLE_HREG": {
            "register": 93,
            "len": 1,
            "val": 19
        }
    },
    "ISTS": {
        "EXAMPLE_ISTS": {
            "register": 67,
            "len": 1,
            "val": 0
        }
    },
    "IREGS": {
        "EXAMPLE_IREG": {
            "register": 10,
            "len": 1,
            "val": 60001
        }
    }
}

"""
# alternatively the register definitions can also be loaded from a JSON file
import json

with open('registers/example.json', 'r') as file:
    register_definitions = json.load(file)
"""

print('Requesting and updating data on RTU client at address {} with {} baud'.format(slave_addr, baudrate))
print()

# READ COILS
coil_address = register_definitions['COILS']['EXAMPLE_COIL']['register']
coil_qty = register_definitions['COILS']['EXAMPLE_COIL']['len']
coil_status = host.read_coils(
    slave_addr=slave_addr,
    starting_addr=coil_address,
    coil_qty=coil_qty)
print('Status of COIL {}: {}'.format(coil_address, coil_status))
time.sleep(1)

# WRITE COILS
new_coil_val = 0
operation_status = host.write_single_coil(
    slave_addr=slave_addr,
    output_address=coil_address,
    output_value=new_coil_val)
print('Result of setting COIL {} to {}'.format(coil_address, operation_status))
time.sleep(1)

# READ COILS again
coil_status = host.read_coils(
    slave_addr=slave_addr,
    starting_addr=coil_address,
    coil_qty=coil_qty)
print('Status of COIL {}: {}'.format(coil_address, coil_status))
time.sleep(1)

print()

# READ HREGS
hreg_address = register_definitions['HREGS']['EXAMPLE_HREG']['register']
register_qty = register_definitions['HREGS']['EXAMPLE_HREG']['len']
register_value = host.read_holding_registers(
    slave_addr=slave_addr,
    starting_addr=hreg_address,
    register_qty=register_qty,
    signed=False)
print('Status of HREG {}: {}'.format(hreg_address, register_value))
time.sleep(1)

# WRITE HREGS
new_hreg_val = 44
operation_status = host.write_single_register(
    slave_addr=slave_addr,
    register_address=hreg_address,
    register_value=new_hreg_val,
    signed=False)
print('Result of setting HREG {} to {}'.format(hreg_address, operation_status))
time.sleep(1)

# READ HREGS again
register_value = host.read_holding_registers(
    slave_addr=slave_addr,
    starting_addr=hreg_address,
    register_qty=register_qty,
    signed=False)
print('Status of HREG {}: {}'.format(hreg_address, register_value))
time.sleep(1)

print()

# READ ISTS
ist_address = register_definitions['ISTS']['EXAMPLE_ISTS']['register']
input_qty = register_definitions['ISTS']['EXAMPLE_ISTS']['len']
input_status = host.read_discrete_inputs(
    slave_addr=slave_addr,
    starting_addr=ist_address,
    input_qty=input_qty)
print('Status of IST {}: {}'.format(ist_address, input_status))
time.sleep(1)

print()

# READ IREGS
ireg_address = register_definitions['IREGS']['EXAMPLE_IREG']['register']
register_qty = register_definitions['IREGS']['EXAMPLE_IREG']['len']
register_value = host.read_input_registers(
    slave_addr=slave_addr,
    starting_addr=ireg_address,
    register_qty=register_qty,
    signed=False)
print('Status of IREG {}: {}'.format(ireg_address, register_value))
time.sleep(1)

print()

# reset all registers back to their default values on the client
# WRITE COILS
print('Resetting register data to default values...')
coil_address = \
    register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['register']
new_coil_val = True
operation_status = host.write_single_coil(
    slave_addr=slave_addr,
    output_address=coil_address,
    output_value=new_coil_val)
print('Result of setting COIL {}: {}'.format(coil_address, operation_status))
time.sleep(1)

print()

print("Finished requesting/setting data on client")
