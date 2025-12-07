# Unified Diagnostic Services (UDS)

DiveCAN uses [UDS (ISO-14229)](https://en.wikipedia.org/wiki/Unified_Diagnostic_Services) for settings/firmware/log dumps.

UDS runs on top of **ISO-TP (ISO-15765-2)** and supports multi-frame transfers, structured data identifiers (DIDs), and memory upload/download operations.

---

## Transport Layer (ISO-TP)

UDS messages are transmitted over ISO-TP using Single Frame (SF), First Frame (FF), Consecutive Frame (CF), and Flow Control (FC) formats.

### ⚠️ Shearwater Flow Control Quirk

Shearwater devices transmit **Flow Control frames with dst = 0xFF**.
This violates ISO-TP. Standards-compliant stacks may reject these frames; DiveCAN implementations must **accept FC frames regardless of DLC**.

---

## Negative Response Codes

Negative responses found:

```text
7F <ServiceID> <ResponseCode>
```

| Code | Name                                        | Description                            |
|------|---------------------------------------------|----------------------------------------|
| `0x10` | `GeneralReject`                             | Generic failure                         |
| `0x13` | `IncorrectMessageLengthOrInvalidFormat`     | Payload length / format is not valid   |
| `0x21` | `BusyRepeatRequest`                         | ECU is busy, caller should retry       |
| `0x22` | `ConditionsNotCorrect`                      | Preconditions not met                  |
| `0x24` | `RequestSequenceError`                      | Request is out of expected sequence    |
| `0x31` | `RequestOutOfRange`                         | Address / DID / value not supported    |
| `0x34` | `AuthenticationRequired`                    | Authentication step missing/failed     |
| `0x72` | `GeneralProgrammingFailure`                 | Programming (flash/NVM) failed         |
| `0x73` | `WrongBlockSequenceCounter`                 | TransferData block counter mismatch    |

---

## UDS Services Used on DiveCAN

The following UDS services are known to be used by SOLO:

| Service                   | Request SID | Response SID | Notes                      |
|---------------------------|-------------|--------------|----------------------------|
| ReadDataByIdentifier      | `0x22`      | `0x62`       | RDBI                       |
| WriteDataByIdentifier     | `0x2E`      | `0x6E`       | WDBI                       |
| RequestDownload           | `0x34`      | `0x74`       | Firmware / data download   |
| RequestUpload             | `0x35`      | `0x75`       | Memory upload / dumping    |
| TransferData              | `0x36`      | `0x76`       | Chunked transfer blocks    |
| TransferExit *(inferred)* | `0x37`      | `0x77`       | End of transfer sequence   |
| Negative Response         | `0x7F`      | —            | Error reporting            |

---

## ReadDataByIdentifier / WriteDataByIdentifier

Both services operate on 16‑bit Data Identifiers (DIDs).

### Request Format

```text
00 <SID> <DID_H> <DID_L> [Payload…]
```

- `SID = 0x22` for ReadDataByIdentifier
- `SID = 0x2E` for WriteDataByIdentifier
- `DID_H`, `DID_L` form a big‑endian 16‑bit DID
- `Payload` is present for write requests (WDBI)

### Response Format

```text
00 <SID+0x40> <DID_H> <DID_L> <Payload…>
```

- `SID = 0x62` for RDBI responses
- `SID = 0x6E` for WDBI responses

Unknown or unsupported DIDs, or invalid access, typically return a negative response with code `RequestOutOfRange (0x31)`.

---

## Known/Seen Data Identifiers (DIDs)

The following DIDs are currently known / suspected from reverse‑engineering:

| DID       | Name                               | Access | Comment                                       |
|-----------|------------------------------------|--------|-----------------------------------------------|
| `0x8010`  | `Unknown`                          | R      | Likely serial-related                         |
| `0x8011`  | `SoftwareVersion`                  | R      | —                                             |
| `0x8020`  | `FirmwareDownload`                 | R      | [0] suppored, [1-4] address, [5-9] length     |
| `0x8021`  | `LogUpload`                        | R      | [0] suppored, [1-4] address, [5-9] length     |
| `0x8200`  | `Serial`                           | R/W    | Device serial number                          |
| `0x8201`  | `Unknown`                          | R      | —                                             |
| `0x8202`  | `Unknown`                          | R/W    | —                                             |
| `0x8203`  | `Unknown`                          | R      | —                                             |
| `0x8204`  | `Unknown`                          | R/W    | —                                             |
| `0x8205`  | `Unknown`                          | R      | Cell ADC calibration probably                 |
| `0x8206`  | `Unknown`                          | R      | —                                             |
| `0x8209`  | `Unknown`                          | R      | Likely firmware checksum/CRC                  |
| `0x820A`  | `Unknown`                          | R      | Battery calibration probably                  |
| `0x820B`  | `Unknown`                          | R      | DES‑encrypted data,                           |
| `0x9100`  | `UserSettingCount`                 | R      | Number of user settings                        |
| `0x9110+i` | `UserSettingInfo(i)`              | R      | Label, type, editable                          |
| `0x9130+i` | `UserSettingValue(i)`             | R      | Value/max for setting `i`                      |
| `0x9150+i+(j<<4)` | `UserSettingLabel(i,j)`    | R      | Label for selection option `j`                 |
| `0x9350`  | `UserSettingSave`                  | W      | Commit settings                                |

`i` and `j` are 4‑bit indices encoded into the DID (see §9).

---

## RequestUpload (Memory Dump)

`RequestUpload (0x35)` is used to **read spi flash data** on SOLO

### Request Format

```text
00 35 00 44 <ADDR32> <SIZE32>
```

- `00`        : DiveCAN UDS address (physical)
- `35`        : `SID_REQUEST_UPLOAD_REQ`
- `00`        : Data Format Identifier (plain)
- `44`        : Address/size length descriptor (4 bytes address, 4 bytes size)
- `<ADDR32>`  : Big‑endian start address
- `<SIZE32>`  : Big‑endian number of bytes requested

### Response Format

```text
00 75 <MaxBlockSize>
```

- `75` is `RequestUpload` response SID
- `MaxBlockSize` is the maximum number of payload bytes returned per `TransferData` block

#### TransferData Request

```text
00 36 <BlockSeq>
```

#### TransferData Response

```text
00 76 <BlockSeq> <Data…>
```

- `BlockSeq` starts at `1` and wraps at `0xFF → 0x00`
- The client keeps sending `TransferData` until:
  - Returned `Data` is empty, or
  - Total byte count reaches requested size, or
  - A negative response is received

### TransferExit

Standard UDS defines `TransferExit (0x37)` to terminate a transfer:

```text
00 37
```

---

## Upload Regions (RequestUpload Address Map)

### Region Summary

| Region     | Virtual Address Range        | Real Address | Notes |
|------------|------------------------------|--------------|-------|
| **BLOCK1** | `0xC2000080` – `0xC2000FFF` | `0x00000080` | Addr align **8**; Size min **8**; Size align **8**; Size max `0xFFFFFFFF` |
| **BLOCK2** | `0xC3001000` – `0xC3FFFFFF` | `0x00010000` | Addr align **0**; Size min **12**; Size align **12**; Size max `0x00FFF000` |
| **BLOCK3** | `0xC5000000` – `0xC500007F` | `UNKNOWN`    | Addr align **0**; Size min **1**; Size align **0**; Size max `0x80` |
> **Note:** The address range is treated as *virtual* by higher-level code; only ranges matching these constraints are accepted by the device. Misaligned or out-of-range requests will typically return `RequestOutOfRange (0x31)`.

---

## RequestDownload (Firmware Upload)

`RequestDownload (0x34)` is the mirror of RequestUpload, used for **writing** firmware to device memory.
Before issuing a RequestDownload, the valid base address and maximum writable length can obtained by reading DID 0x8020 (FirmwareDownload)

### Request Format

```text
00 34 00 44 <ADDR32> <SIZE32>
```

Same header semantics as RequestUpload:

- `34` is `RequestDownload` request SID
- `00` / `44` specify plain format and 4+4 byte address/size

---

## User Settings (Menu System)

User settings are exposed via the `0x91xx` DID range and encode setting indices directly in the DID.

### DID Encoding

| Type              | Base DID   | Encoding                        |
|-------------------|-----------:|---------------------------------|
| SettingCount      | `0x9100`   | —                               |
| SettingInfo(i)    | `0x9110`   | `0x9110 + i`                    |
| SettingValue(i)   | `0x9130`   | `0x9130 + i`                    |
| SettingLabel(i,j) | `0x9150`   | `0x9150 + i + (j << 4)`         |
| SettingSave       | `0x9350`   | —                               |

Where:

- `i` = setting index (0–15 encoded in low nibble)
- `j` = option index (selection variants; encoded in high nibble)

### Payload Formats

#### SettingCount (`0x9100`)

```text
<count: u8>
```

Number of available settings.

#### SettingInfo(i) (`0x9110 + i`)

```text
<label bytes…> <kind: u8> <editable: u8>
```

- `label`    : raw bytes, usually ASCII or UTF‑8
- `kind`     :
  - `0` = Text
  - `1` = Selection
  - `2` = Number
- `editable` : `0` = read‑only, `1` = editable

#### SettingValue(i) (`0x9130 + i`)

```text
<max: u64 BE> <current: u64 BE>
```

- `max`     : maximum allowed numeric value
- `current` : current setting value

For non‑numeric settings (e.g. selections), `current` is used as an index into the available options.

#### SettingLabel(i,j) (`0x9150 + i + (j << 4)`)

```text
<label bytes…>
```

Human‑readable label for the selection option `j` of setting `i`.

Setting labels are only used for `Selection` type settings, and are not required for `Text` / `Number`.

#### SettingSave (`0x9350`)

Exact payload semantics are not fully decoded.  
Observed behavior suggests that a write to this DID triggers a **commit of pending setting changes** to non‑volatile memory.

---