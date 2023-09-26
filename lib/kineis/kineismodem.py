import board
import asyncio
import digitalio
import busio
import json
from kineis.encoder import Iridium, Header
import time
import binascii

# IO2 = 10 = RX_modem/TX_EP, IO1 = 11  = TX_modem/RX_EP Pins = (Tx,RX,RTS,CTS)  version 1

debug = True

class M_controller:
    def __init__(self):
        self.sat_list = []
        self.done = True

class message:
    def __init__(self,modem,data,bytes,priority = 1, tries = 1, waittime = 60, burst = 1, bursttime = 1, tx_wait = 0):
        self.data = data
        self.bytes = bytes
        self.priority = priority
        self.tries = tries*priority
        self.waittime = waittime/priority
        self.burst = burst
        self.bursttime = bursttime
        self.timer = tx_wait * waittime
        self.bursttries = burst
        modem.message_list.append(self)
        if debug: print("message queued to be sent {0} times after {1} minutes".format(self.tries,self.waittime))

class modem:

    uart = busio.UART(board.IO10, board.IO11, baudrate=9600)
    on_off = digitalio.DigitalInOut(board.IO9)
    on_off.direction = digitalio.Direction.OUTPUT
    time2transmit = 0
    
    def __init__(self):
        self.lock = asyncio.Lock()
        self.on_off.value = True
        self.message_list = []
        if debug: print('modem initialized')
        self.at_test()

    def sendCommand(self,sentence):
        msg = sentence + '\n'
        self.uart.write(bytes(msg,'utf-8'))
        if debug: print('message sent: ',msg)

    def transmitData(self,data,bytes = 23):
        msg = 'AT+TX='+ hex(data)[2:]
        if bytes > 23:
            raise ValueError("Message is bigger than modem's capacity") 
        if self.time2transmit == 0:
            self.sendCommand(msg)
        else: print("Tried to transmit before safe time")
        self.time2transmit = 60         # no se puede transmitir dos veces sin 60 segundos en el medio
    
    def at_test(self):
        self.sendCommand('AT+PING=?')

    def turnOff(self):
        self.on_off.value = False

    def getKineisID(self):
        self.sendCommand('AT+ID=?')

    def getTXfreq(self):
        self.sendCommand('AT+ATXFRQ=?')

    def getTXfmt(self):
        self.sendCommand('AT+AFMT=?')

    def handler(self,_msg):
        msg = _msg.decode('utf-8')
        if debug: print('received: ',msg)

    async def messageManager(self):
        while True:
            # saco los mensajes que ya se enviaron
            sent = False
            self.message_list = [message for message in self.message_list if message.tries > 0]
            for message in self.message_list:
                if (message.timer == 0) and (sent == False):
                    self.transmitData(message.data, message.bytes)
                    if message.bursttries > 1:
                        message.timer = message.bursttime
                        message.bursttries -= 1
                    else:
                        message.timer = message.waittime
                        message.tries -= 1
                        message.bursttries = message.burst
                    sent = True
                    if debug:
                        if message.tries == 0:
                            print('This was the last transmission')
                        else:                        
                            print('Next transmission of this message will be in ' + str(message.timer) + ' minutes')
                if message.timer > 0:
                    message.timer -= 1
            await asyncio.sleep_ms(60000)
    
    async def transmissionTime(self):
        while True:
            if self.time2transmit > 0:
                self.time2transmit -= 1
            await asyncio.sleep_ms(1000)

    async def checkUnsolicited(self,wait_time):
        while True:
            if self.uart.in_waiting:
                self.handler(self.uart.readline())
            else:
                await asyncio.sleep_ms(wait_time)
    
async def test(test_hours):

    kineisModem = modem()
    #kineisModem.sendCommand('AT+AFMT=1')
    await asyncio.sleep_ms(2000)
    asyncio.create_task(kineisModem.checkUnsolicited(1000))
    asyncio.create_task(kineisModem.transmissionTime())
    asyncio.create_task(kineisModem.messageManager())
    await asyncio.sleep_ms(2000)
    trama1 = Iridium()
    Header(trama1,[15,15,len(kineisModem.message_list),10,0,0,0,1])
    reporte1, bitsize1 = trama1.encode()
    m1 = message(modem = kineisModem, data = reporte1, bytes = bitsize1//8 , priority = 1 , tries = test_hours, burst=4, bursttime = 3)
    while True:
        print("tries:", m1.tries, "burst tries:", m1.bursttries)
        await asyncio.sleep_ms(30000)

asyncio.run(test(10))
