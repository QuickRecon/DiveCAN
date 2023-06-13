# DiveCAN
DiveCAN is Shearwater's proprietary bus for allowing rebreather components (such as dive computers, solenoids, and oxygen monitoring systems) to communicate. This system is built on top of the already well established CANBus, which has proven reliable in many other automotive and industrial environments. Shearwater has stated that they will not support homebrew development using this platform, however it is a proven digital communications system for rebreathers and with the advent of solid state cells there is a need for a digital communications bus to streamline integration. Therefore the bus has been reverse engineered and the results presented in this repository.

The data captures logic analyser CAN exports used to compile this information can be found under `Data Captures/`.

As this repository is based on inherently incomplete data, be sure to validate all of the information presented before relying on it in a life support system. There are absolutely things that have been missed and those things may cause unexpected behavior including but not limited to erroneous PPO2 readings, incorrect solenoid behavior, and other unforeseen problems.

## The bus
The bus is a 125kbps CAN bus running at an ~3v logic level (3.0v CAN high, 2.0v CAN idle, 0.0v CAN low, sampled from a rEvo battery box). Unlike the standard 120 ohm terminating resistor for normal CAN systems DiveCAN uses a 560 ohm resistor on each terminating device. Furthermore according to [divebandits.de](https://www.divebandits.de/en/training/iart/rebreather/bus-systems/70-rebreather-with-a-bus-part-2.html) it is only possible to connect 9 devices. Further details about the hardware configuration can be found under `Hardware/`.

## The protocol
From observations it appears that DiveCAN does not use a secondary layer on top of DiveCAN to abstract the data (such as CANOpen) and is transmitting the raw data over the CAN protocol using different messages, with each message having a different extended ID. All IDs observed lie in the `0x0dxxxxxx` block with different ranges corresponding to different types of message, for example the `0x0ddxxxxx` range is used for exchanging device serial numbers. Further details about the messaging protocol is found under `Messaging/`.

## The architecture
Shearwaters implementation offloads almost all of the work for managing the CCR onto the DiveCAN node in the head of the rebreather (controller) with the shearwater acting only as a display/interface. The controller has the following major responsibilities (identified so far):
- Convert millivolts to PPO2, transmit both to display.
- Fire the solenoid to maintain the setpoint prescribed by the display.
- Flag error states for the display such as solenoid failures, as well as low battery.
- Perform cell voting and calculation of consensus value.
- Calibrate the cells when told by the display, update internal calibration coefficients.

The shearwater computers perform very little (none found) error/sanity checking on the values provided by the controller, and display what is sent over the bus even if that information is contradictory (for example 0.99 PPO2 with 0mV cells).

## Testing
As it is only a 125kbps bus it is very tolerant of mistreatment with regards to termination resistors and differential impedance matching, and the CANLow transition can be sampled with a simple logic analyser. Furthermore it is tolerant to higher than standard voltage transitions, so an [Arduino CAN shield](https://www.keyestudio.com/2019new-keyestudio-can-bus-shield-mcp2551-chip-with-sd-socket-for-arduino-uno-r3-p0543.html) can be used for read/write on the bus. This hardware was used for testing/demonstration of the reverse engineered protocol, further details found under `Testing/`.


# TO DO
- Document messaging protocol
- Demo selectable options in menu
- Demo multiple devices on bus
- Make more datacaptures on different units
- Identify connector/vendor