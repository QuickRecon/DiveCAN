# Protocol

The PPO2 messaging over DiveCAN is handled using 3 seperate messages, firstly the PPO2 from each cell is sent. Then the millivolts from each cell, then finally a cell status message is sent. This cell status message contains the status mask for the cells as well as the "average" or consensus PPO2 that the computer uses for decompression calculation.

| Message       | CAN ID        | Length        | Purpose       |
| ------------- | ------------- | ------------- | ------------- |
| PPO2          | 0xD040004     | 4             | Transmit per-cell PPO2 information |
| Millivolts    | 0xD110004     | 7             | Transmit per-cell millivolt information |
| Cell Status   | 0xDCA0004     | 2             | Transmit information about cell status and consensus value |

It is important to note that there is no relationship between PPO2, millivolts, and the consensus value on the handset side of the system. Values are used and displayed verbatim as they come over the bus with no form of consistency checking between messages.

# PPO2
ID: 0xD040004

Byte 0 is always 0x0 and no apparent effects have been observed modifying this value.

Bytes 1 - 3 represent the cell PPO2 as a 8 bit integer, for example a PPO2 of 1.32 would be 132 (0x84). The exception to this is the value 0xFF, which will cause the value to display as "FAIL" on the monitor. If all cells are 0xFF then the computer will display "Needs Cal".

| Byte          | Value         |
| ------------- | ------------- |
| 0             | 0x0           |
| 1             | Cell 1 PPO2   |
| 2             | Cell 2 PPO2   |
| 3             | Cell 3 PPO2   |

## Example
A message representing a PPO2 of [0.58, 0.66, 0.67]:
```
CAN: Start of frame
CAN: Identifier: 833 (0x341)
CAN: Substitute remote request: 1
CAN: Identifier extension bit: extended frame
CAN: Extended Identifier: 4 (0x4)
CAN: Full Identifier: 218365956 (0xd040004)
CAN: Remote transmission request: data frame
CAN: Reserved bit 1: 0
CAN: Reserved bit 0: 0
CAN: Data length code: 4
CAN: Data byte 0: 0x00
CAN: Data byte 1: 0x3a
CAN: Data byte 2: 0x42
CAN: Data byte 3: 0x43
CAN: CRC-15 sequence: 0x20e8
CAN: CRC delimiter: 1
CAN: ACK slot: ACK
CAN: ACK delimiter: 1
CAN: End of frame
```


# Millivolts
ID: 0xD110004

Bytes 0-5 are the cell millivolts, transmitted as big-endian 16 bit integers. For example 53.24 mV would be expressed as 5324 (0x14 0xCC).

Byte 6 is always 0x0 and no apparent effects have been observed modifying this value.

| Byte          | Value             |
| ------------- | -------------     |
| 0-1           | Cell 1 Millivolts |
| 2-3           | Cell 2 Millivolts |
| 4-5           | Cell 3 Millivolts |
| 6             | 0x0               |

## Example
A message representing a millivolts of [11.36, 10.80, 11.35]:

```
CAN: Start of frame
CAN: Identifier: 836 (0x344)
CAN: Substitute remote request: 1
CAN: Identifier extension bit: extended frame
CAN: Extended Identifier: 65540 (0x10004)
CAN: Full Identifier: 219217924 (0xd110004)
CAN: Remote transmission request: data frame
CAN: Reserved bit 1: 0
CAN: Reserved bit 0: 0
CAN: Data length code: 7
CAN: Data byte 0: 0x04
CAN: Data byte 1: 0x70
CAN: Data byte 2: 0x04
CAN: Data byte 3: 0x38
CAN: Data byte 4: 0x04
CAN: Data byte 5: 0x6f
CAN: Data byte 6: 0x00
CAN: CRC-15 sequence: 0x25df
CAN: CRC delimiter: 1
CAN: ACK slot: ACK
CAN: ACK delimiter: 1
CAN: End of frame
```

# Cell Status
ID: 0xDCA0004

Byte 0 is the status mask for the cells, it is a 3 bit number where each 1 in the binary representation indicates of a cell is ok. Cell 1 is given the value 0b1, Cell 2 has 0b10, and Cell 3 has 0b100. If all is operating normally then the value is 0b111. However if (for example) cell 1 is faulty then the mask would be 0b110. If a 0 bit is sent then the cell field is marked in yellow on the handset, this is typically to indicate an outlier or cell that has been excluded from the voting logic.

Byte 1 is the consensus PPO2 value represented as an 8 bit integer, it is the value that the computer uses for decompression calculations and is typically an average of the cells included in the voting logic.

| Byte          | Value           |
| ------------- | -------------   |
| 0             | Status Mask     |
| 1             | Consensus Value |

## Example
A message representing 3 good cells and a consensus PPO2 of 0.38: 

```
CAN: Start of frame
CAN: Identifier: 882 (0x372)
CAN: Substitute remote request: 1
CAN: Identifier extension bit: extended frame
CAN: Extended Identifier: 131076 (0x20004)
CAN: Full Identifier: 231342084 (0xdca0004)
CAN: Remote transmission request: data frame
CAN: Reserved bit 1: 0
CAN: Reserved bit 0: 0
CAN: Data length code: 2
CAN: Data byte 0: 0x07
CAN: Data byte 1: 0x26
CAN: CRC-15 sequence: 0x5205
CAN: CRC delimiter: 1
CAN: ACK slot: ACK
CAN: ACK delimiter: 1
CAN: End of frame
```

# Ambient Pressure
ID: 0xD080000

Atmospheric pressure in millibar.

Bytes 0-1 are the int16 value in big-endian format.

The remainder of the packet is unknown

| Byte          | Value           |
| ------------- | -------------   |
| 0-1           | Ambient Pressure|

## Example
```
11970036-11970059 CAN: Fields: Start of frame
11970060-11970323 CAN: Fields: Identifier: 834 (0x342)
11970324-11970347 CAN: Fields: Substitute remote request: 1
11970348-11970371 CAN: Fields: Identifier extension bit: extended frame
11970372-11970875 CAN: Fields: Extended Identifier: 1 (0x1)
11970372-11970875 CAN: Fields: Full Identifier: 218628097 (0xd080001)
11970876-11970899 CAN: Fields: Remote transmission request: data frame
11970900-11970923 CAN: Fields: Reserved bit 1: 0
11970924-11970947 CAN: Fields: Reserved bit 0: 0
11970948-11971043 CAN: Fields: Data length code: 5
11971044-11971259 CAN: Fields: Data byte 0: 0x03
11971260-11971474 CAN: Fields: Data byte 1: 0xf5
11971475-11971690 CAN: Fields: Data byte 2: 0x03
11971691-11971906 CAN: Fields: Data byte 3: 0xf6
11971907-11972122 CAN: Fields: Data byte 4: 0x01
11972123-11972482 CAN: Fields: CRC-15 sequence: 0x6b89
11972483-11972506 CAN: Fields: CRC delimiter: 1
11972508-11972531 CAN: Fields: ACK slot: ACK
11972532-11972555 CAN: Fields: ACK delimiter: 1
11972556-11972723 CAN: Fields: End of frame
```

# Setpoint

ID: 0xDC90000

Byte 0 is the setpoint the controller is to hold.

| Byte          | Value           |
| ------------- | -------------   |
| 0             | Setpoint        |

## Example
```
11937138-11937161 CAN: Fields: Start of frame
11937162-11937425 CAN: Fields: Identifier: 882 (0x372)
11937426-11937449 CAN: Fields: Substitute remote request: 1
11937450-11937473 CAN: Fields: Identifier extension bit: extended frame
11937474-11937976 CAN: Fields: Extended Identifier: 65537 (0x10001)
11937474-11937976 CAN: Fields: Full Identifier: 231276545 (0xdc90001)
11937977-11938000 CAN: Fields: Remote transmission request: data frame
11938001-11938024 CAN: Fields: Reserved bit 1: 0
11938025-11938048 CAN: Fields: Reserved bit 0: 0
11938049-11938168 CAN: Fields: Data length code: 1
11938169-11938360 CAN: Fields: Data byte 0: 0x13
11938361-11938719 CAN: Fields: CRC-15 sequence: 0x5587
11938720-11938743 CAN: Fields: CRC delimiter: 1
11938744-11938767 CAN: Fields: ACK slot: ACK
11938768-11938791 CAN: Fields: ACK delimiter: 1
11938792-11938959 CAN: Fields: End of frame
```