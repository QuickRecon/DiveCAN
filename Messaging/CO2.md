# Co2 Value
ID: 0xD210004

Byte 0-1 is the CO2 concentration gas in ppm, in little endian format with 0x0120 = 8193, 0 is reserved for no-data, so 0x0100 results in a zero value

| Byte          | Value                           |
| ------------- | -------------                   |
| 0- 1          | PCO2 value in Little Endian     |



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