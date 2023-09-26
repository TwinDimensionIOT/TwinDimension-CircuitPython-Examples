import struct
from collections import OrderedDict

header = OrderedDict({
    'destino':4,   
    'origen':4,
    'secuencia':8,
    'longitud':8,
    'hardware':4,
    'project':4,
    'COT':3,
    'Quantity':3
})

m1 = OrderedDict({
    'length':8,      
    'DI':1
})

m2 = OrderedDict({
    'length':8,      
    'presence':1,
    'type':1,
    'counterDI1':32,
    'counterDI2':64
})

m3 = OrderedDict({
    'length':8,      
    'presence':1,
    'type':1,
    'ontime1':32,
    'ontime2':64
})

m4 = OrderedDict({
    'length':8,
    'type':3, 
    'timestamp':32

})

m5 = OrderedDict({
    'length':5,      
    'indexD':6,
    'DI':1,
    'indexA':6,
    'type':3,
    'timestamp':32,
})

m6 = OrderedDict({
    'length':5,      
    'index':6,
    'DI':1,
    'timestamp':32,
})

analog_types = OrderedDict({
    't0':16,     
    't1':16,
    't2':32,
    't3':32,
    't4':32
})

class Iridium():
    
    def __init__(self):
        self.messages = []

    # Agrego un uno adelante de todo para no perder los ceros del primer campo
    # Codifico todos los mensajes que haya en la cola
    # Despues agrego el offset tal que sea divisible por 8 y saco el primer 1
    def encode(self):
        frame = 1
        for message in self.messages:
            frame = message.encode_m(frame)
        while (get_bit_length(frame) % 8) != 1:
            frame <<= 1
        mask = ((1 << (get_bit_length(frame)-1)) - 1)
        bitsize = get_bit_length(frame)-1
        frame &= mask
        return frame, bitsize

class Header():
    def __init__(self,frame,values):
        self.frame = frame
        self.values = values
        self.frame.messages.append(self)
    
    def encode_m(self,frame):
        result = frame
        if (self.values[0] == 15) and (self.values[1] == 15):
            for i in range(len(header)):
                #print('value:' ,self.values[i], ' , lenght: ',header[list(header)[i]])
                result = add2frame(result,self.values[i],header[list(header)[i]])
        else:
            for i in range(4):
                result = add2frame(result,self.values[i],header[list(header)[i]]) 
        return result

class Message1():
    def __init__(self, frame, length, values):
        self.frame = frame
        self.length = length
        self.values = values
        self.frame.messages.append(self)

    def encode_m(self,frame):
        result = frame
        result = add2frame(result,self.length,m1['length'])
        for i in range(self.length):
            result = add2frame(result,self.values[i],m1['DI'])
        return result
    
class Message2():
    def __init__(self, frame, length, presence, types, values):
        self.frame = frame
        self.length = length
        self.presence = presence
        self.types = types
        self.values = values
        self.frame.messages.append(self)

    def encode_m(self,frame):
        result = frame
        result = add2frame(result,self.length,m2['length'])
        for i in range(self.length):
            present = self.presence[i]
            result = add2frame(result,present,m2['presence'])
            if present == 1:
                counter_type = self.types[i]
                result = add2frame(result,counter_type,m2['type'])
                if counter_type == 0:
                      result = add2frame(result,self.values[i],m2['counterDI1'])
                elif counter_type == 1:
                    result = add2frame(result,self.values[i],m2['counterDI2'])   
                else:
                    raise ValueError
        return result

class Message3():
    def __init__(self, frame, length, presence, types, values):
        self.frame = frame
        self.length = length
        self.presence = presence
        self.types = types
        self.values = values
        self.frame.messages.append(self)

    def encode_m(self,frame):
        result = frame
        result = add2frame(result,self.length,m3['length'])
        for i in range(self.length):
            present = self.presence[i]
            result = add2frame(result,present,m3['presence'])
            if present == 1:
                counter_type = self.types[i]
                result = add2frame(result,counter_type,m3['type'])
                if counter_type == 0:
                      result = add2frame(result,self.values[i],m3['ontime1'])
                elif counter_type == 1:
                    result = add2frame(result,self.values[i],m3['ontime2'])   
                else:
                    raise ValueError
        return result

class Message4():
    def __init__(self, frame, length, types, values, timestamp):
        if len(types) != len(values):
            raise ValueError('No coinciden cantidad de tipos y la cantidad de valores')
        self.frame = frame
        self.length = length
        self.types = types
        self.values = values
        self.timestamp = timestamp
        self.frame.messages.append(self)
    
    def encode_m(self,frame):
        result = frame
        result = add2frame(result,self.length,m4['length'])
        for i in range(self.length):
            result = add2frame(result,self.types[i],m4['type'])
            value, a_type = get_analog(self.types[i],self.values[i]) 
            add2frame(result,value,a_type)
        result = add2frame(result,self.timestamp,m4['timestamp'])
        return result
    
class Message5():
    def __init__(self, frame, length, indecesD, DIs, indecesA, types, values, timestamps):
        self.frame = frame
        self.length = length
        self.indecesD = indecesD
        self.DIs = DIs
        self.indecesA = indecesA
        self.types = types
        self.values = values
        self.timestamps = timestamps
        self.frame.messages.append(self)

    def encode_m(self,frame):
        result = frame
        result = add2frame(result,self.length,m5['length'])
        for i in range(self.length):
            result = add2frame(result,self.indecesD[i],m5['indexD'])
            result = add2frame(result,self.DIs[i],m5['DI'])
            result = add2frame(result,self.indecesA[i],m5['indexA'])
            result = add2frame(result,self.types[i],m5['type'])
            value, a_type = get_analog(self.types[i],self.values[i]) 
            add2frame(result,value,a_type)
            result = add2frame(result,self.timestamps[i],m5['timestamp'])
        return result
    
class Message6():
    def __init__(self, frame, length, indecesD, DIs, timestamps):
        self.frame = frame
        self.length = length
        self.indecesD = indecesD
        self.DIs = DIs
        self.timestamps = timestamps
        self.frame.messages.append(self)

    def encode_m(self,frame):
        result = frame
        result = add2frame(result,self.length,m2['length'])
        for i in range(self.length):
            result = add2frame(result,self.indecesD[i],m6['index'])
            result = add2frame(result,self.DIs[i],m6['DI'])
            result = add2frame(result,self.timestamps[i],m6['timestamp'])
        return result


def add2frame(frame,value,bits):
    result = frame
    if (value >> bits): # no existe bit_lenght() en upython / value.bit_length() > bits:
        raise ValueError('No entra ese valor en esa cantidad de bits')
    else:
        result <<= bits
        mask = ((1 << bits) - 1)
        result |= (value & mask)
        return result
    
def get_analog(type_value, value):
    if type_value == 0:
        return int.from_bytes((struct.pack('>H',value)), 'big'),analog_types['t0']
    elif type_value == 1:
        return int.from_bytes((struct.pack('>h',value)), 'big'),analog_types['t1']
    elif type_value == 2:
        return int.from_bytes((struct.pack('>I',value)), 'big'),analog_types['t2']
    elif type_value == 3:
        return int.from_bytes((struct.pack('>i',value)), 'big'),analog_types['t3']
    elif type_value == 4:
        return int.from_bytes((struct.pack('>f',value)), 'big'),analog_types['t4']
    else:
        raise TypeError
    
def get_bit_length(number):
    i = 0
    while (number >> i):
        i += 1
    return i

def main():

    trama = Iridium()
    Header(trama,[15,15,255,10,0,0,0,1])
    #Header(trama,[0,0,1,10])
    Message1(trama,2,[1,1])
    Message2(trama,4,[1,0,0,0],[0,0,0,1],[4294967295,10,10,10])
    Message4(trama,1,[4],[3.1415],1024)
    Message4(trama,5,[0,1,2,3,4],[1,-1,1,-1,2.0],1024)
    Message6(trama,2,[32,32],[1,1],[1024,1024])
    reporte, bitsize = trama.encode()
    print("{:b}".format(reporte))
    print(bitsize)
    report_bytes =reporte.to_bytes(bitsize//8,'big')
    print(report_bytes.hex())


if __name__ == "__main__":
    main()