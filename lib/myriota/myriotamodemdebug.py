
import board
import asyncio
import digitalio
import busio

# IO2 = 10 = RX_modem/TX_EP, IO1 = 11  = TX_modem/RX_EP Pins = (Tx,RX,RTS,CTS)  version 1

debug = True

class modem:

    uart = busio.UART(board.IO10, board.IO11, baudrate=9600)
    query_cmd_list = ["MSGQ", "STATE", "VSDK", "MID", "REGCODE", "TIME", "LOCATION", "SUSPEND"]
    control_cmd_list = ["SAVEMSG", "TXSTART", "TXSTOP", "GNSSFIX", "RSSI", "SMSG", "SUSPEND"]

    def __init__(self):
        self.lock = asyncio.Lock()

    def sendCommand(self,sentence):
        msg = sentence + '\n'
        self.uart.write(bytes(msg,'utf-8'))
        if debug: print('message sent: ',msg)

    def transmitData(self,data,bytes = 23):
        payload = data.to_bytes(bytes,'big').hex()
        msg = 'AT+SMSG='+ payload    
        if len(payload) > 40:
            raise ValueError(" The message is bigger than what is supported") 
        self.sendCommand(msg)
    
    def test(self):
        self.sendCommand('AT')

    def SendQueryCommand(self, command):
        self.sendCommand('AT+'+command+'=?')
    
    def SendControlCommand(self, command, parameter = ""):
        if parameter != "":
            self.sendCommand('AT+'+command+'='+parameter)
        else:
            self.sendCommand('AT+'+command)

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
        for cmd in kineisModem.query_cmd_list:
            #await asyncio.sleep_ms(1000)
            kineisModem.SendQueryCommand(cmd)
        await asyncio.sleep_ms(15000)
        
if __name__ == "__main__":

    asyncio.run(test())


