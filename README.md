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
| `0x02`     | Unknown (sent/received by handset)                   |
| `0x03`     | Unknown (sent/received by handset)                   |
| `0x04`     | [PPO2](Messaging/PPO2.md#ppo2)                       |
| `0x07`     | Unknown (probably ext battery voltage)               |
| `0x08`     | Unknown (sent by handset)                            |
| `0x0A`     | ISO-TP/CANFD frame (TODO)                            |
| `0x0B`     | Unknown (sent by handset)                            |
| `0x10`     | NOP (ignored by handset)                             |
| `0x11`     | [Millivolt](Messaging/PPO2.md#millivolts)            |
| `0x12`     | [Calibration response](Messaging/Calibration.md#calibration-response) |
| `0x13`     | [Calibration init](Messaging/Calibration.md#calibration-init) |
| `0x20`     | Unknown (sent by handset)                            |
| `0x30`     | Unknown (sent by handset)                            |
| `0x37`     | [BusInit](Messaging/Device%20Metadata.md#bus-init)   |
| `0xC1`     | Unknown (recv by handset)                            |
| `0xC3`     | Unknown (sent by handset)                            |
| `0xC4`     | Unknown (sent by handset)                            |
| `0xC9`     | Unknown (sent by handset)                            |
| `0xCA`     | [Cell status](Messaging/PPO2.md#cell-status)         |
| `0xCB`     | [Status](Messaging/Device%20Metadata.md#status)      |
| `0xCC`     | Unknown (sent by handset)                            |
| `0xD2`     | [Serial](Messaging/Device%20Metadata.md#serial)      |

## Testing
As it is only a 125kbps bus it is very tolerant of mistreatment with regards to termination resistors and differential impedance matching, and the CANLow transition can be sampled with a simple logic analyser. Furthermore it is tolerant to higher than standard voltage transitions, so an [Arduino CAN shield](https://www.keyestudio.com/2019new-keyestudio-can-bus-shield-mcp2551-chip-with-sd-socket-for-arduino-uno-r3-p0543.html) can be used for read/write on the bus. This hardware was used for testing/demonstration of the reverse engineered protocol, further details found under `Demo/`.


# TO DO
- Demo selectable options in menu
- Demo multiple devices on bus
- Make more datacaptures on different units
