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

# Example
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
