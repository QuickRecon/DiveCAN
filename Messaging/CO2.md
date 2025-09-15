# Co2 Calibration request
ID: 0xD230004

Byte 0-1 is the CO2 calibration gas in millibar?, in big endian format with 0xfd1 = 400 0x3761 = 1400, maybe multiplied by ambient pressure to get

| Byte          | Value         |
| ------------- | ------------- |
| 01             | 0x0          |
| 1             | Cell 1 PPO2   |
| 2             | Cell 2 PPO2   |
| 3             | Cell 3 PPO2   |

## Examples
```
t+46.74568 | rx id: 0xd230401; 0f,d1,
t+235.75949 | rx id: 0xd230401; 37,61,
```