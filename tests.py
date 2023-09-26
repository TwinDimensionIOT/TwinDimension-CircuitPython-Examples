import time
import board
from analogio import AnalogIn
import digitalio
import microcontroller
import busio

time_interval = 0.5

analog_in = AnalogIn(board.IO12)

def get_voltage(pin):
    return (pin.value * 3.3) / 65536

def test_voltage_measure():
    while True:
        print(get_voltage(analog_in))
        time.sleep(time_interval)

led = digitalio.DigitalInOut(board.IO41)
led.direction = digitalio.Direction.OUTPUT

def test_blink():
    while True:
        led.value = True
        time.sleep(time_interval)
        led.value = False
        time.sleep(time_interval)
        
def test_temperature_measure():
    while True:
        print(microcontroller.cpu.temperature)
        time.sleep(time_interval)
         

i2c = busio.I2C(board.IO11, board.IO10)  
   
def i2c_scan():
    while True:
        print("I2C addresses:",[hex(device) for device in i2c.scan()])
        time.sleep(2)
   
#test_blink()
test_voltage_measure()
#test_temperature_measure()