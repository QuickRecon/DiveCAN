# Tank Pressure
ID: 0xD0B0004

Transmits HP pressures to the handsets for units that support it. Some evidence to suggest this is sent by handset, however when this happens is unknown

Byte 0 determines whether the transmission is O2 or diluent. 0x00 implies O2, 0x10 implies Diluent.

Bytes 1-2 is the pressure in decibar, 0x0203 = 51.5 bar (displayed as 52 bar)

| Byte          | Value               |
| ------------- | -------------       |
| 0             | Cylinder designator |
| 1-2           | Pressure (decibar)  |