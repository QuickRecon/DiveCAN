# DiveCAN
DiveCAN is Shearwater's proprietary bus for allowing rebreather components (such as dive computers, solenoids, and oxygen monitoring systems) to communicate. This system is built on top of the already well established CANBus, which has proven reliable in many other automotive and industrial environments. Shearwater has stated that they will not support homebrew development using this platform, however it is a proven digital communications system for rebreathers and with the advent of solid state cells there is a need for a digital communications bus to streamline integration. Therefore the bus has been reverse engineered and the results presented in this repository.

The data captures logic analyser CAN exports used to compile this information can be found under `Data Captures/`.

As this repository is based on inherently incomplete data, be sure to validate all of the information presented before relying on it in a life support system. There are absolutely things that have been missed and those things may cause unexpected behavior including but not limited to erroneous PPO2 readings, incorrect solenoid behavior, and other unforeseen problems.

## The bus
The bus is a 125kbps CAN bus running at an ~3v logic level (3.0v CAN high, 2.0v CAN idle, 0.0v CAN low, sampled from a rEvo battery box). Unlike the standard 120 ohm terminating resistor for normal CAN systems DiveCAN uses a 560 ohm resistor on each terminating device. Furthermore according to [divebandits.de](https://www.divebandits.de/en/training/iart/rebreather/bus-systems/70-rebreather-with-a-bus-part-2.html) it is only possible to connect 9 devices. Further details about the hardware configuration can be found under `Hardware/`.

## The protocol
From observations it appears that DiveCAN does not use a secondary layer on top of DiveCAN to abstract the data (such as CANOpen) and is transmitting the raw data over the CAN protocol using different messages, with each message having a different extended ID. All IDs observed lie in the `0x0dxxxxxx` block with different ranges corresponding to different types of message, for example the `0x0ddxxxxx` range is used for exchanging device serial numbers. Further details about the messaging protocol is found under `Messaging/`.

The extended ID can be broken down like this
```
 31              24 23      16 15           8 7        0
+----------------+----------+---------------+----------+
|   chan (0x0D)  | msg_type | params/dst_id |  src_id  |
|    (5 bits)    | (8 bits) |    (8 bits)   | (8 bits) |
+----------------+----------+---------------+----------+
```


## The architecture
Shearwaters implementation offloads almost all of the work for managing the CCR onto the DiveCAN node in the head of the rebreather (controller) with the shearwater acting only as a display/interface. The controller has the following major responsibilities (identified so far):
- Convert millivolts to PPO2, transmit both to display.
- Fire the solenoid to maintain the setpoint prescribed by the display.
- Flag error states for the display such as solenoid failures, as well as low battery.
- Perform cell voting and calculation of consensus value.
- Calibrate the cells when told by the display, update internal calibration coefficients.

The shearwater computers perform very little (none found) error/sanity checking on the values provided by the controller, and display what is sent over the bus even if that information is contradictory (for example 0.99 PPO2 with 0mV cells).

## Variation between devices
While yet to be confirmed at a larger scale, different rebreathers (or items on a rebreather) change the least significant bit in the message IDs. An incomplete list of observed "device IDs" is:

| ID            | Device         |
| ------------- | -------------  |
| 1             | Shearwater controller |
| 2             | JJ OBOE, ISC Pathfinder head |
| 3             | JJ HUD |
| 4             | JJ SOLO, Optima head  |
| 5             | rEvo Battery Box  |

Devices sharing an ID will behave identically with different controllers, this has been validated for JJ controllers operating a CM O2pima rebreather, it is expected that this generalizes. For example a JJ HUD should be able to read an ISC Pathfinder bus. This repo uses IDs 1 and 4 as most data captures were taken from a Shearwater controller and JJ SOLO.

### DiveCAN message types

| `msg_type` | Function                                             |
|------------|------------------------------------------------------|
| `0x00`     | [Id](Messaging/Device%20Metadata.md#id)              |
| `0x01`     | [Name](Messaging/Device%20Metadata.md#name)          |
| `0x02`     | [Unknown metadata](Messaging/Device%20Metadata.md#Unknown-metadata)                                             |
| `0x03`     | [Shutdown](Messaging/Device%20Metadata.md#shutdown)  | 
| `0x04`     | [PPO2](Messaging/PPO2.md#ppo2)                       |
| `0x07`     | [HUD Status](Messaging/Device%20Metadata.md#hud-status) |
| `0x08`     | [Ambient Pressure](Messaging/PPO2.md#ambient-pressure) |
| `0x0A`     | ISO-TP/CANFD frame (TODO, part of [menu system](Messaging/Bus%20Devices%20Menu.md))|
| `0x0B`     | [Tank Pressure](Messaging/Pressure.md#tank-pressure) |
| `0x10`     | NOP (ignored by handset)                             |
| `0x11`     | [Millivolt](Messaging/PPO2.md#millivolts)            |
| `0x12`     | [Calibration response](Messaging/Calibration.md#calibration-response) |
| `0x13`     | [Calibration init](Messaging/Calibration.md#calibration-init) |
| `0x20`     | [CO2 Status](Messaging/CO2.md#co2-enabled)           |
| `0x21`     | [CO2](Messaging/CO2.md#co2-value)                    |
| `0x22`     | [CO2 Calibration Response](Messaging/CO2.md#co2-calibration-response) |
| `0x23`     | [CO2 Calibration Init](Messaging/CO2.md#co2-calibration-request) |
| `0x30`     | Unknown (sent by handset) (TODO, part of [menu system](Messaging/Bus%20Devices%20Menu.md)) |
| `0x37`     | [BusInit](Messaging/Device%20Metadata.md#bus-init)   |
| `0xC1`     | Unknown (recv by handset, sending results in 0xC4 back with 0x00 payload)                            |
| `0xC3`     | Unknown (sent by handset)                            |
| `0xC4`     | Unknown (sent by handset)                            |
| `0xC9`     | [Setpoint](Messaging/PPO2.md#setpoint)               |
| `0xCA`     | [Cell status](Messaging/PPO2.md#cell-status)         |
| `0xCB`     | [Status](Messaging/Device%20Metadata.md#status)      |
| `0xCC`     | [Diving](Messaging/Device%20Metadata.md#diving)      |
| `0xD2`     | [Serial](Messaging/Device%20Metadata.md#serial)      |

## Testing
As it is only a 125kbps bus it is very tolerant of mistreatment with regards to termination resistors and differential impedance matching, and the CANLow transition can be sampled with a simple logic analyser. Furthermore it is tolerant to higher than standard voltage transitions, so an [Arduino CAN shield](https://www.keyestudio.com/2019new-keyestudio-can-bus-shield-mcp2551-chip-with-sd-socket-for-arduino-uno-r3-p0543.html) can be used for read/write on the bus. This hardware was used for testing/demonstration of the reverse engineered protocol, further details found under `Demo/`.


# A note on captures
There are 2 formats of capture in use under `Data Captures/`. The format of:
```11937138-11937161 CAN: Fields: Start of frame
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
12277050-12277073 CAN: Fields: Start of frame
12277074-12277337 CAN: Fields: Identifier: 836 (0x344)
12277338-12277361 CAN: Fields: Substitute remote request: 1
12277362-12277385 CAN: Fields: Identifier extension bit: extended frame
12277386-12277865 CAN: Fields: Extended Identifier: 65540 (0x10004)
12277386-12277865 CAN: Fields: Full Identifier: 219217924 (0xd110004)
12277866-12277889 CAN: Fields: Remote transmission request: data frame
12277890-12277913 CAN: Fields: Reserved bit 1: 0
12277914-12277937 CAN: Fields: Reserved bit 0: 0
12277961-12278056 CAN: Fields: Data length code: 7
12278057-12278272 CAN: Fields: Data byte 0: 0x04
12278273-12278464 CAN: Fields: Data byte 1: 0xb5
12278465-12278680 CAN: Fields: Data byte 2: 0x04
12278681-12278872 CAN: Fields: Data byte 3: 0xd0
12278873-12279088 CAN: Fields: Data byte 4: 0x05
12279089-12279280 CAN: Fields: Data byte 5: 0x6a
12279281-12279496 CAN: Fields: Data byte 6: 0x00
12279497-12279855 CAN: Fields: CRC-15 sequence: 0x48e6
12279856-12279879 CAN: Fields: CRC delimiter: 1
12279881-12279904 CAN: Fields: ACK slot: ACK
12279905-12279928 CAN: Fields: ACK delimiter: 1
12279929-12280096 CAN: Fields: End of frame
```

Represents data captured from real hardware network using a logic analyser, for example in `Data Captures/JJ Cal OK.txt`. The other form is:

```t+3.36959 | RX id: 0xd000001; 01,00,97,
t+6.02012 | TX id: 0xd010004; 43,2d,69,6e,61,74,6f,72,
t+6.02022 | TX id: 0xdcb0004; 50,00,00,00,00,46,63,00,
t+6.02028 | TX id: 0xd040004; 00,30,30,30,
t+6.02033 | TX id: 0xd110004; 04,70,04,38,04,6f,00,
t+6.02037 | TX id: 0xd000004; 00,00,00,
t+6.02042 | TX id: 0xdca0004; 07,46,
t+6.02046 | TX id: 0xd210004; 01,01,10,
t+7.86541 | TX id: 0xd220004; 01,01,00,
t+8.36054 | RX id: 0xd000001; 01,00,97,
t+9.02658 | TX id: 0xd010004; 43,2d,69,6e,61,74,6f,72,
t+9.02666 | TX id: 0xdcb0004; 50,00,00,00,00,46,63,00,
t+9.03708 | TX id: 0xd040004; 00,30,30,30,
t+9.05768 | TX id: 0xd110004; 04,70,04,38,04,6f,00,
t+9.07827 | TX id: 0xd000004; 00,00,00,
t+9.09919 | TX id: 0xdca0004; 07,46,
t+9.11982 | TX id: 0xd210004; 01,01,10,
t+9.71534 | RX id: 0xdc90001; 46,
t+9.73223 | RX id: 0xd080001; 04,05,04,07,01,
```
This represents data captured using the code under `PythonTester/`, for example `Data Captures/CO2CalFail400ppm.txt`. For this format the "head" side of the network is simulated in the script and the handsets' response (RX in the log) is the only data being produced by Shearwater hardware/software. This form allows for specific situations to be simulated, but may not accurately represent the behavior of a real system.

# TO DO
- Demo selectable options in menu
- Demo multiple devices on bus
- Make more datacaptures on different units
