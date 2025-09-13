# Protocol
Calibration values within a DiveCAN system stores the coefficients on the head, rather than in the computer. The handset is completely "out of band" with the calibration process and simply signals when the process should begin and listens for the appropriate responses.

The calibration protocol has not been fully explored however sufficient information is known to run the "happy path" of a calibration reliably. The dialog is composed of a few steps:

1. The shearwater initializes a calibration by sending a 0xD130201 message. This message contains the FO2 of the diluent and the ambient pressure as measured by the shearwater,
2. The head sends a calibration acknowledgement message 0xD120004. This causes the shearwater to go into the calibration screen.
3. The millivolt values on the shearwater continues to update via the usual millivolt messaging as the calibration process goes on. There is a minimum interval of approximately 1 second at this screen before the shearwater will allow the process to continue.
4. When the calibration is complete the head sends a calibration complete message 0xD120004 which contains the millivolts of each cell, the FO2, and the pressure. It is these values that gets logged in the calibration history of the computer.

 Message               | Origin        | CAN ID        | Length        | Purpose       |
| ------------         | ------------- | ------------- | ------------- | ------------- |
| Calibration Init     | Handset       | 0xD130201     | 3             | Sent by the shearwater when it becomes active on the bus, repeatedly broadcast until response or timeout |
| Calibration Response | Head          | 0xD120004     | 8             | Sent by the head to inform the handset of calibration status and response |

# Calibration Init
ID: 0xD130201

This message is sent when the shearwater goes into calibration mode, where it waits for the cal ack and then subsequent calibration result screen. If this message is not responded to the shearwater will eventually timeout with an appropriate error message.

Byte 0 is the FO2 of the calibration gas in the usual form (eg 0x63 is 0.99).

Byte 1-2 is the pressure transmitted as big-endian 16 bit integer, eg 0x0400 would be 1024 millibar.


| Byte          | Value                |
| ------------- | -------------        |
| 0             | FO2                  |
| 1-2           | Atmospheric pressure |

## Example
A calibration request with a 100% FO2 and 1014mB of atmospheric pressure:

```
CAN: Start of frame
CAN: Fields: Full Identifier: 219349505 (0xd130201)
CAN: Fields: Remote transmission request: data frame
CAN: Fields: Reserved bit 1: 0
CAN: Fields: Reserved bit 0: 0
CAN: Fields: Data length code: 3
CAN: Fields: Data byte 0: 0x64
CAN: Fields: Data byte 1: 0x03
CAN: Fields: Data byte 2: 0xf6
CAN: Fields: CRC-15 sequence: 0x2146
CAN: Fields: CRC delimiter: 1
CAN: Fields: ACK slot: ACK
CAN: Fields: ACK delimiter: 1
CAN: Fields: End of frame
```

# Calibration Response
ID: 0xD120004

This message is sent when the head informs the handset of a change in calibration status, byte 0 in the message indicates what type of message it is. 

| Byte 0 | Meaning         |
| ------ | --------------- |
| 0x01   | Success         |
| 0x05   | Ack             |
| 0x08   | Rejected        |
| 0x10   | Low ext. batt   |
| 0x18   | Solenoid error  |
| 0x20   | Fo2 range error |
| 0x28   | Pressure error  |

## Ack
Ack is the initial response to the handset request to calibrate and must be sent after a request to calibrate, otherwise the shearwater will timeout on the request. The fields for the Ack appear to be invariant and are as per the example.

## Result
The result is sent after the calibration is complete, it must be sent no less than 1 second after the ack.

Bytes 1-3 of the ack is the millivolts expressed as a 8 bit int, eg 0x33 is 51mV.

Byte 4 is the FO2 in same format as the request

Byte 5-6 is the atmospheric pressure in the same form as the request.

Byte 7 is always 0x07. It is unknown what effect varying this value has.


| Byte          | Value         |
| ------------- | ------------- |
| 0             | Message Type  |
| 1             | C1 Millis     |
| 2             | C2 Millis     |
| 3             | C3 Millis     |
| 4             | FO2           |
| 5-6           | Atmo Pressure |
| 7             | 0x07          |


## Example
A calibration ack observed by a JJ.

```
CAN: Start of frame
CAN: Fields: Full Identifier: 219283460 (0xd120004)
CAN: Fields: Remote transmission request: data frame
CAN: Fields: Reserved bit 1: 0
CAN: Fields: Reserved bit 0: 0
CAN: Fields: Data length code: 8
CAN: Fields: Data byte 0: 0x05
CAN: Fields: Data byte 1: 0x00
CAN: Fields: Data byte 2: 0x00
CAN: Fields: Data byte 3: 0x00
CAN: Fields: Data byte 4: 0xff
CAN: Fields: Data byte 5: 0xff
CAN: Fields: Data byte 6: 0xff
CAN: Fields: Data byte 7: 0x00
CAN: Fields: CRC-15 sequence: 0x18bf
CAN: Fields: CRC delimiter: 1
CAN: Fields: ACK slot: ACK
CAN: Fields: ACK delimiter: 1
CAN: Fields: End of frame
```

Calibration complete observed by a JJ:
```
CAN: Fields: Start of frame
CAN: Fields: Identifier: 832 (0x340)
CAN: Fields: Substitute remote request: 1
CAN: Fields: Identifier extension bit: extended frame
CAN: Fields: Extended Identifier: 4 (0x4)
CAN: Fields: Full Identifier: 219283460 (0xd120004)
CAN: Fields: Remote transmission request: data frame
CAN: Fields: Reserved bit 1: 0
CAN: Fields: Reserved bit 0: 0
CAN: Fields: Data length code: 8
CAN: Fields: Data byte 0: 0x01
CAN: Fields: Data byte 1: 0x34
CAN: Fields: Data byte 2: 0x32
CAN: Fields: Data byte 3: 0x34
CAN: Fields: Data byte 4: 0x64
CAN: Fields: Data byte 5: 0x03
CAN: Fields: Data byte 6: 0xf6
CAN: Fields: Data byte 7: 0x07
CAN: Fields: CRC-15 sequence: 0x6b81
CAN: Fields: CRC delimiter: 1
CAN: Fields: ACK slot: ACK
CAN: Fields: ACK delimiter: 1
CAN: Fields: End of frame
```