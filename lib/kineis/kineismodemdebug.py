
import board
import asyncio
import digitalio
import busio

# IO2 = 10 = RX_modem/TX_EP, IO1 = 11  = TX_modem/RX_EP Pins = (Tx,RX,RTS,CTS)  version 1

debug = True

class modem:

    uart = busio.UART(board.IO10, board.IO11, baudrate=9600)
    on_off = digitalio.DigitalInOut(board.IO9)
    on_off.direction = digitalio.Direction.OUTPUT
    time2transmit = 0

    def __init__(self):
        self.lock = asyncio.Lock()
        self.on_off.value = True

    def sendCommand(self,sentence):
        msg = sentence + '\n'
        self.uart.write(bytes(msg,'utf-8'))
        if debug: print('message sent: ',msg)

    def transmitData(self,data,bytes = 23):
        msg = 'AT+TX='+data.to_bytes(bytes,'big').hex()    
        if bytes > 23:
            raise ValueError(" El mensaje es mas grande de lo que permite el modem") 
        if self.time2transmit == 0:
            self.sendCommand(msg)
        self.time2transmit = 60         # no se puede transmitir dos veces sin 60 segundos en el medio
    
    def test(self):
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

    async def checkUnsolicited(self,wait_time):
        while True:
            if self.uart.in_waiting:
                self.handler(self.uart.readline())
            else:
                await asyncio.sleep_ms(wait_time)

def receive_input(modem):
    while True:
        rx = input() 
        modem.sendCommand(rx) 
        
async def test():

    kineisModem = modem()
    asyncio.create_task(kineisModem.checkUnsolicited(1000))
    while True:
        kineisModem.test()
        kineisModem.getKineisID()
        kineisModem.getTXfreq()
        kineisModem.getTXfmt()
        await asyncio.sleep_ms(15000)
        
if __name__ == "__main__":

    asyncio.run(test())


