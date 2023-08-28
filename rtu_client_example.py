"""
Main script

Do your stuff here, this file is similar to the loop() function on Arduino

Create a Modbus RTU client (slave) which can be requested for data or set with
specific values by a host device.

The RTU communication pins can be choosen freely (check MicroPython device/
port specific limitations).
The register definitions of the client as well as its connection settings like
bus address and UART communication speed can be defined by the user.
"""

# import modbus client classes
import board
from umodbus.serial import ModbusRTU

# ===============================================
# RTU Slave setup
# act as client, provide Modbus data via RTU to a host device
# ModbusRTU can get serial requests from a host device to provide/set data
# check MicroPython UART documentation
# https://docs.micropython.org/en/latest/library/machine.UART.html
# for Device/Port specific setup
#
# For further details check the latest MicroPython Modbus RTU documentation
# example https://micropython-modbus.readthedocs.io/en/latest/EXAMPLES.html#rtu

tx_pin=board.IO13            # tx pin
rx_pin=board.IO48            # rx pin
de_not_re_pin=board.IO14     # control DE/RE
slave_addr=100
baudrate=9600

client = ModbusRTU(
    tx_pin=tx_pin,      # tx pin
    rx_pin=rx_pin,      # rx pin
    addr=slave_addr,    # address on bus
    baudrate=baudrate,  # optional, default 9600
    # data_bits=8,      # optional, default 8
    # stop_bits=1,      # optional, default 1
    # parity=None,      # optional, default None
    de_not_re_pin=de_not_re_pin,  # optional, control DE/RE
    #re_de_delay=1000,   # optional, re to de delay (us)
    #de_re_delay=1000,   # optional, de to re delay (us)
)


def reset_data_registers_cb(reg_type, address, val):
    # usage of global isn't great, but okay for an example
    global client
    global register_definitions

    print('Resetting register data to default values ...')
    client.setup_registers(registers=register_definitions)
    print('Default values restored')


# common slave register setup, to be used with the Master example above
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
            "register": 0,
            "len": 10,
            "val": [1,2,3,4,5,6,7,8,9,10]
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

# reset all registers back to their default value with a callback
register_definitions['COILS']['RESET_REGISTER_DATA_COIL']['on_set_cb'] = \
    reset_data_registers_cb

print('Setting up registers ...')
# use the defined values of each register type provided by register_definitions
client.setup_registers(registers=register_definitions)
# alternatively use dummy default values (True for bool regs, 999 otherwise)
# client.setup_registers(registers=register_definitions, use_default_vals=True)
print('Register setup done')

print('Serving as RTU client on address {} at {} baud'.
      format(slave_addr, baudrate))

while True:
    try:
        result = client.process()
    except KeyboardInterrupt:
        print('KeyboardInterrupt, stopping RTU client...')
        break
    except Exception as e:
        print('Exception during execution: {}'.format(e))

print("Finished providing/accepting data as client")
