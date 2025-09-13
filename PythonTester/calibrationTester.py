# Test calibration responses on the handset

import can
import time, threading
import asyncio

can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'can0'
can.rc['bitrate'] = 125000

def txID(bus):
    msg = can.Message(
        arbitration_id=0xD000004,
        data=[0x00, 0x00, 0x00],
        is_extended_id=True
    )
    try:
        bus.send(msg)
        #print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        #print("Message NOT sent")
        global busFailed
        busFailed = True

def txName(bus):
    name = "C-inator"
    byte_name = bytearray()
    byte_name.extend(map(ord, name))


    msg = can.Message(
        arbitration_id=0xD010004,
        data=byte_name,
        is_extended_id=True
    )
    try:
        bus.send(msg)
        #print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        #print("Message NOT sent")
        global busFailed
        busFailed = True

def txStatus(bus):
    msg = can.Message(
        arbitration_id=0xDCB0004,
        data=[0x50, 0x00, 0x00, 0x00, 0x00, 0x46, 0x63, 0x00],
        is_extended_id=True
    )
    try:
        bus.send(msg)
        #print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        #print("Message NOT sent")
        global busFailed
        busFailed = True

def txPPO2(bus):
    msg = can.Message(
        arbitration_id=0xD040004,
        data=[0x00, 0x20, 0x20, 0x20],
        is_extended_id=True
    )
    try:
        bus.send(msg)
        #print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        #print("Message NOT sent")
        global busFailed
        busFailed = True

def txMillis(bus):
    msg = can.Message(
        arbitration_id=0xD110004,
        data=[0x04,0x70,0x04,0x38,0x04,0x6f,0x00],
        is_extended_id=True
    )
    try:
        bus.send(msg)
        #print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        #print("Message NOT sent")
        global busFailed
        busFailed = True   

def txCellStat(bus):
    msg = can.Message(
        arbitration_id=0xDCA0004,
        data=[0b111, 0x46],
        is_extended_id=True
    )
    try:
        bus.send(msg)
        #print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        #print("Message NOT sent")
        global busFailed
        busFailed = True

def txCalAck(bus):
    msg = can.Message(
        arbitration_id=0xD120004,
        data=[0x05, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x00],
        is_extended_id=True
    )
    try:
        bus.send(msg)
        #print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        #print("Message NOT sent")
        global busFailed
        busFailed = True

def txCalResp(bus, err):
    msg = can.Message(
        arbitration_id=0xD120004,
        data=[err, 0x32, 0x31, 0x33, 0x64, 0x03, 0xf6, 0x07],
        is_extended_id=True
    )
    try:
        bus.send(msg)
        #print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        #print("Message NOT sent")
        global busFailed
        busFailed = True


# The bare minimum to convince the shearwater that we're real
def ping(bus):
    txID(bus)
    txName(bus)
    txStatus(bus)
    txPPO2(bus)
    txMillis(bus)
    txCellStat(bus)


# Global state storage
swConnected = False
calibrating = False
pinging = True
printMsgs = True

startTime = time.time()
def print_message(msg: can.Message) -> None:
    """Regular callback function. Can also be a coroutine."""
    if printMsgs:
        currTime = time.time()
        deltaT = currTime - startTime
        deltaTStr = "{:.5f}".format(deltaT)
        hex_string = "".join("%02x," % b for b in msg.data)
        print("t+"+deltaTStr+" | rx id: " + hex(msg.arbitration_id)+"; "+ hex_string)
    if msg.arbitration_id == 0xD000001:
        global swConnected
        swConnected = True
    if msg.arbitration_id == 0xD130401:
        global calibrating
        calibrating = True

with can.ThreadSafeBus() as bus: 
    can.Notifier(bus, [print_message], loop=None)

    def pingTimer():
        ping(bus)
        #print("ping!")
        if(pinging):
            threading.Timer(1, pingTimer).start()

    pingTimer()

    while not swConnected:
        for msg in bus:
            print("Shearwater Connected")
            swConnected = True
            break
    
    while not calibrating:
        for msg in bus:
            if msg.arbitration_id == 0xD130401:
                print("Recieved Calibration Request")
                calibrating = True
                break

    txCalAck(bus)
    time.sleep(4)
    txCalResp(bus, 0x28)