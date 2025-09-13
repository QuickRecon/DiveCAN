# Protocol

There are a number of "maintenance" items that occurs on the bus that does not convey any diving/state information but is necessary for the proper functioning of the bus. For example identifying the items on the bus and notifying devices of a power-on event, as well as internal pings/status messaging to detect a dropped link. 

 Message       | Origin        | CAN ID        | Length        | Purpose       |
| ------------ | ------------- | ------------- | ------------- | ------------- |
| Bus Init     | Handset       | 0xD370401     | 3             | Sent by the shearwater when it becomes active on the bus, repeatedly broadcast until response or timeout |
| ID           | Handset/Head  | 0xD000001/4   | 3             | The device ID, the shearwater (probably) has an internal lookup to compare this ID with capabilities (solenoid, cell, etc), also has version number for firmware. |
| Name         | Head          | 0xD010004     | 8             | Transmit the name of the device, can be anything (that fits), displayed in bus devices menu |
| Status       | Head          | 0xDCB0004     | 8             | Status of the device, has ext battery voltage and error code|
| Serial       | Head/HUD/Bat  | 0xDD20003     | 8             | ASCII string of device serial number

# Bus Init
ID: 0xD370401

Byte 0 is always 0xa8.

Byte 1 is always 0xf3.

Byte 2 is always 0x00.

Very little is known about what this message actually means with regards to its content, shearwater patch notes indicate it should be possible to use this message to turn on the shearwater from the head but more experimentation is needed.

| Byte          | Value         |
| ------------- | ------------- |
| 0             | 0x8a          |
| 1             | 0xf3          |
| 2             | 0x00          |

## Example
Message from shearwater startup (while connected to JJ):
```
CAN: Fields: Start of frame
CAN: Fields: Identifier: 845 (0x34d)
CAN: Fields: Substitute remote request: 1
CAN: Fields: Identifier extension bit: extended frame
CAN: Fields: Extended Identifier: 197633 (0x30401)
CAN: Fields: Full Identifier: 221709313 (0xd370401)
CAN: Fields: Remote transmission request: data frame
CAN: Fields: Reserved bit 1: 0
CAN: Fields: Reserved bit 0: 0
CAN: Fields: Data length code: 3
CAN: Fields: Data byte 0: 0xa8
CAN: Fields: Data byte 1: 0xf3
CAN: Fields: Data byte 2: 0x00
CAN: Fields: CRC-15 sequence: 0x29db
CAN: Fields: CRC delimiter: 1
CAN: Fields: ACK slot: NACK
CAN: Fields: ACK delimiter: 0
CAN: Fields: End of frame
```

# ID
ID: 0xD000001/4

The last digit of the message ID is the device ID, device IDs confer capabilities to other devices on the network, devices that share an ID present the same capabilities and are intercompatible. The found device IDs so far are:

| ID            | Device         |
| ------------- | -------------  |
| 1             | Shearwater controller |
| 2             | JJ OBOE, ISC Pathfinder head |
| 3             | JJ HUD |
| 4             | JJ SOLO, Optima head  |
| 5             | rEvo Battery Box  |

Byte 0 is the manufacturer ID, values are as tabled.

Byte 1 is always 0x00, the effects of changing this value are to be determined.

Byte 2 is the firmware version on the identing device, for example the shearwater firmware version on message 0xD000001.

| Manufacturer ID | Manufacturer                          |
| ------------- | -------------                           |
| 0x1           | Shearwater Research International (SRI) |
| All Others    | General (GEN)                           |

| Byte          | Value         |
| ------------- | ------------- |
| 0             | Manufacturer          |
| 1             | 0x00          |
| 2             | Firmware Version          |

## Example
Message from shearwater running version 84:
```
CAN: Fields: Start of frame
CAN: Fields: Identifier: 832 (0x340)
CAN: Fields: Substitute remote request: 1
CAN: Fields: Identifier extension bit: extended frame
CAN: Fields: Extended Identifier: 1 (0x1)
CAN: Fields: Full Identifier: 218103809 (0xd000001)
CAN: Fields: Remote transmission request: data frame
CAN: Fields: Reserved bit 1: 0
CAN: Fields: Reserved bit 0: 0
CAN: Fields: Data length code: 3
CAN: Fields: Data byte 0: 0x01
CAN: Fields: Data byte 1: 0x00
CAN: Fields: Data byte 2: 0x84
CAN: Fields: CRC-15 sequence: 0x673a
CAN: Fields: CRC delimiter: 1
CAN: Fields: ACK slot: ACK
CAN: Fields: ACK delimiter: 1
CAN: Fields: End of frame
```

# Name
ID: 0xD010004

Bytes 0-7 is the name that gets sent ot the shearwater and is displayed in the bus devices menu, it can be up to 8 characters long and does not need to be null terminated. It uses ASCII codepoints, it is not known what the effect of sending non-ASCII or non-printable chars is.


| Byte          | Value          |
| ------------- | -------------  |
| 0-7           | Name as Chars  |

## Example
Message from JJ SOLO:
```
CAN: Fields: Start of frame
CAN: Fields: Identifier: 832 (0x340)
CAN: Fields: Substitute remote request: 1
CAN: Fields: Identifier extension bit: extended frame
CAN: Fields: Extended Identifier: 65540 (0x10004)
CAN: Fields: Full Identifier: 218169348 (0xd010004)
CAN: Fields: Remote transmission request: data frame
CAN: Fields: Reserved bit 1: 0
CAN: Fields: Reserved bit 0: 0
CAN: Fields: Data length code: 8
CAN: Fields: Data byte 0: 0x53
CAN: Fields: Data byte 1: 0x4f
CAN: Fields: Data byte 2: 0x4c
CAN: Fields: Data byte 3: 0x4f
CAN: Fields: Data byte 4: 0x20
CAN: Fields: Data byte 5: 0x32
CAN: Fields: Data byte 6: 0x20
CAN: Fields: Data byte 7: 0x20
CAN: Fields: CRC-15 sequence: 0x6495
CAN: Fields: CRC delimiter: 1
CAN: Fields: ACK slot: ACK
CAN: Fields: ACK delimiter: 1
CAN: Fields: End of frame
```

# Status
ID: 0xDCB0004

Byte 0 is the battery voltage expressed as an integer representing 00.0V, for example 0x0F would be 1.5V.

Bytes 1-4 varies in an unknown way.

Byte 5 appears to be the setpoint that the head is attempting to maintain in the form 0.00, eg 0x46 would be a PPO2 of 0.70.

Byte 6 varies in an unknown way.

Byte 7 is the device error code, the values as tabled. Error codes can be ORed together to display a combination of errors. A solenoid error, once sent, appears to persist until the shearwater is turned off and on again. Higher value error codes have been observed (and tested) however they do not present a message to their user so the use is unknown.

| Error Code    | Error Message   |
| ------------- | -------------   |
| 0x01          | Low Ext Battery |
| 0x04          | Solenoid Err    |



| Byte          | Value           |
| ------------- | -------------   |
| 0             | Battery Voltage |
| 1-4           | Unknown         |
| 5             | Setpoint        |
| 6             | Unknown         |
| 7             | Error code      |

## Example
Message from JJ SOLO:
```
CAN: Fields: Start of frame
CAN: Fields: Identifier: 836 (0x344)
CAN: Fields: Substitute remote request: 1
CAN: Fields: Identifier extension bit: extended frame
CAN: Fields: Extended Identifier: 65540 (0x10004)
CAN: Fields: Full Identifier: 231407620 (0xdcb0004)
CAN: Fields: Remote transmission request: data frame
CAN: Fields: Reserved bit 1: 0
CAN: Fields: Reserved bit 0: 0
CAN: Fields: Data length code: 8
CAN: Fields: Data byte 0: 0x5b
CAN: Fields: Data byte 1: 0x00
CAN: Fields: Data byte 2: 0x02
CAN: Fields: Data byte 3: 0x00
CAN: Fields: Data byte 4: 0x00
CAN: Fields: Data byte 5: 0x46
CAN: Fields: Data byte 6: 0x63
CAN: Fields: Data byte 7: 0x08
CAN: Fields: CRC-15 sequence: 0x2d84
CAN: Fields: CRC delimiter: 1
CAN: Fields: ACK slot: ACK
CAN: Fields: ACK delimiter: 1
CAN: Fields: End of frame
```

# Serial
ID: 0xDD20003

Serial number as 8 ASCII chars.

| Byte          | Value            |
| ------------- | ---------------  |
| 0-7           | Serial as Chars  |

## Example
```
CAN: Fields: Start of frame
CAN: Fields: Identifier: 884 (0x374)
CAN: Fields: Substitute remote request: 1
CAN: Fields: Identifier extension bit: extended frame
CAN: Fields: Extended Identifier: 131075 (0x20003)
CAN: Fields: Full Identifier: 231866371 (0xdd20003)
CAN: Fields: Remote transmission request: data frame
CAN: Fields: Reserved bit 1: 0
CAN: Fields: Reserved bit 0: 0
CAN: Fields: Data length code: 8
CAN: Fields: Data byte 0: 0x43
CAN: Fields: Data byte 1: 0x41
CAN: Fields: Data byte 2: 0x30
CAN: Fields: Data byte 3: 0x30
CAN: Fields: Data byte 4: 0x31
CAN: Fields: Data byte 5: 0x36
CAN: Fields: Data byte 6: 0x38
CAN: Fields: Data byte 7: 0x33
CAN: Fields: CRC-15 sequence: 0x64d4
CAN: Fields: CRC delimiter: 1
CAN: Fields: ACK slot: ACK
CAN: Fields: ACK delimiter: 1
CAN: Fields: End of frame
```