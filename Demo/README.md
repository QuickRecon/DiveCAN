This is a simple demo program that acts as a DiveCAN solenoid board from a JJ CCR. Note that this code was written as a demo/testing environment for DiveCAN messaging, it is not designed for diving use.

# Software prerequisites
This demo was made in the Arduino IDE and makes use of the [mcp_can](https://github.com/coryjfowler/MCP_CAN_lib/tree/master) library to send and receive data on the bus. Ensure the Arduino is configured to use a 16MHz clock.

# Hardware prerequisites
This demo runs on an Arduino Uno with the [CAN shield](https://www.keyestudio.com/2019new-keyestudio-can-bus-shield-mcp2551-chip-with-sd-socket-for-arduino-uno-r3-p0543.html). The GND, CANLow, and CANHigh header pins on the shield are wired to the corresponding Ground, CanLow, and CANHigh pins of the DiveCAN connector (see `Hardware/` for more details about connector pinout).