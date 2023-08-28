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

## Usage Example

## Documentation

Documentation for this library can be found [here]()

## Contributing

Contributions are welcome! Please read our [Code of Conduct]() before contributing to help this project stay welcoming.
