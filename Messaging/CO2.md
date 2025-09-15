# Co2 Value
ID: 0xD210004

Byte 0 seems to have no effect
Byte 0-1 is the CO2 concentration gas in mBar, in big endian format

| Byte          | Value           |
| ------------- | -------------   |
| 0             | Status?         |
| 1-2           | PCO2 value      |



# Co2 Calibration response
ID: 0xD220004

Byte 0 is the calibration response, if it is 1 then the calibration succeeded, any non-zero response is interpreted as a fail.

Byte 1-2 is latest CO2 sample value

| Byte          | Value                           |
| ------------- | -------------                   |
| 0             | Calibration Ok                  |
| 1-2           | Value at end of calibration     |



# Co2 Calibration request
ID: 0xD230004

Byte 0-1 is the CO2 calibration gas in millibar?, in big endian format with 0xfd1 = 400 0x3761 = 1400, maybe multiplied by ambient pressure to get

| Byte          | Value                           |
| ------------- | -------------                   |
| 0- 1          | PCO2 calibration value          |

## Examples
```
t+46.74568 | rx id: 0xd230401; 0f,d1,
t+235.75949 | rx id: 0xd230401; 37,61,
```