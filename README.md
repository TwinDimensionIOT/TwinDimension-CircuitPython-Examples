# TwinDimension CircuitPython Examples

[![Discord](https://img.shields.io/discord/1016500444379496478)](https://discord.com/channels/1016500444379496478)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin&logoColor=white)](https://www.linkedin.com/company/twindimension)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Twin Dimension | Ready to run examples for our EP family products

---------------

## Dependencies

This driver depends on:

* [Adafruit CircuitPython](https://github.com/adafruit/circuitpython)

Please ensure that all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
[the Adafruit library and driver bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle).

## Contents

* lib
    * adafruit_mcp2515 -> [MCP2515 CAN bus controller](https://docs.circuitpython.org/projects/mcp2515/en/latest/)
    * adafruit_minimqtt -> [MQTT Client library](https://docs.circuitpython.org/projects/minimqtt/en/latest/)
    * j1939 -> [SAE J1939 support for CircuitPython developers](https://github.com/TwinDimensionIOT/TwinDimension-CircuitPython-J1939)
    * tdata -> [T.Data API helper for CircuitPython](https://github.com/TwinDimensionIOT/TwinDimension-CircuitPython-TData)
    * umodbus -> [CircuitPython Modbus RTU Slave/Master and TCP Server/Slave library](https://github.com/TwinDimensionIOT/TwinDimension-CircuitPython-Modbus)
    * adafruit_logging.mpy
* code.py
* j1939_own_ca_producer.py
* j1939_simple_receive_global.py
* rtu_client_example.py -> Modbus Slave
* rtu_client_internals.py -> Modbus Slave (exposing internals. to work in conjunction with rtu_host_to_tdata.py)
* rtu_host_example.py -> Modbus master
* rtu_host_to_tdata.py -> Modbus master to T>Data
* secrets.py -> WiFi & T>Data secrets (ssid, password, token's)
* settings.toml -> 
* tdata_device_api.py -> T>Data device API (single device)
* tdata_gateway_api.py -> T>Data gateway API (multiple device's)
* wifi.py ->
* wifi_scan.py -> 

## Installing

To install the latest version of our firmware you have to download it from the [releases](https://github.com/TwinDimensionIOT/twinpython/releases) from our circuitpython port repository. Then, make sure you have python and esptool installed (you can verify this by running python --version and pip show esptool in the windows console). Open the console on the folder where you downloaded the firmware and run the following command.

* python -m esptool --chip esp32s3 --port YOUR_COM_PORT write_flash -z 0 THE FIRMWARE_BINARY_NAME

For example:

* python -m esptool --chip esp32s3 --port COM4 write_flash -z 0 twindimension_ep_esp32_s3_n8r2_824.bin

Once it finishes, you are done installing the firmware.

## Usage Example

The EP motherboard has 9 general purpose pins that will be used by the different members of the EP family, one pin dedicated to measure the input voltage, one RS-485 interface, a USB interface, wifi connectivity and BLE connectivity. 

Some examples are showed below

```python
#example to blink the on-board led

import board
import digitalio
import time

time_interval = 0.5

led = digitalio.DigitalInOut(board.IO41)
led.direction = digitalio.Direction.OUTPUT

def test_blink():
    while True:
        led.value = True
        time.sleep(time_interval)
        led.value = False
        time.sleep(time_interval)

test_blink()
```

```python
#example to measure the input voltage in the upmost connector

import time
import board
from analogio import AnalogIn

time_interval = 0.5

analog_in = AnalogIn(board.IO12)

def get_voltage(pin):
    return (pin.value * 3.3) / 65536

def test_voltage_measure():
    while True:
        print(get_voltage(analog_in))
        time.sleep(time_interval)

test_voltage_measure()

```

## Documentation

Documentation for this library can be found [here]()

## Contributing

Contributions are welcome! Please read our [Code of Conduct]() before contributing to help this project stay welcoming.
