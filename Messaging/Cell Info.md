# Protocol

> [!WARNING]
> **Source & confidence.**  Nothing here has yet been confirmed against a working system

Separate from the [UDS](UDS.md)/[Bus Devices Menu](Bus%20Devices%20Menu.md) path (msg type
`0x0A`), the handset has a **dedicated request/response sub-protocol on message types
`0x32`–`0x40`** for reading detailed per–O2-cell information from the controller: the cell's
description / part string, manufacturer, serial number, install date, computed age in days,
temperature, and a stored **calibration-record history**. This backs the handset's per-cell
detail screen (titled *"O2 Cell 1/2/3"*, with fields *description*, *Mfgr*, *S/N*, *Temp.*,
cell age in days or *"Exp."*, and *Last Cal.*). It is most likely the readout path for
**solid-state / digital O2 cells** that expose identity and calibration history.

The handset addresses a controller (the "head") and refers to up to **three cells** by a cell
index `0..2` in `Data[0]` of every message. Requests are sent by the handset; the controller
answers with the matching response opcode. All multi-byte fields are **big-endian**.

| Message                | Origin     | CAN ID (ctrl id 4) | Length | Purpose |
| ---------------------- | ---------- | ------------------ | ------ | ------- |
| Cell Read Request      | Handset    | `0xD340401`        | 4      | Request an info field or a cal record for a cell |
| Cell Info Response     | Controller | `0xD350004`        | 3–8    | Field payload (string chars / dates / cal record values) |
| Cell Record Write      | Handset    | `0xD360401`        | 5      | Write a value into a cell record |
| Cell Record Query      | Handset    | `0xD380401`        | 1      | Start record enumeration for a cell |
| Cell Record Ack        | Controller | `0xD390004`        | ≥3     | Acknowledge; returns the record cursor |
| Cell Record Select     | Handset    | `0xD400401`        | 3      | Set the record cursor |
| Cell Temperature       | Controller | `0xD320004`        | 3      | Per-cell temperature |
| Cell Live Value        | Controller | `0xD330004`        | 3      | Per-cell live value (ppO2?), also prompts a metadata refresh |

> ExtID recap (see [top-level README](../README.md)): `[chan 0xD][msg_type][params/dst][src]`.
> For the requests the handset is `src = 0x01` and `dst = controller id` (shown as `4` above);
> for the responses `src = controller id` and the params byte follows the controller-origin
> convention of `0x00` seen on Name/Status/Calibration — **not capture-confirmed for these
> opcodes**.

## Field ids

The **Cell Read Request** (`0x34`) and **Cell Info Response** (`0x35`) address individual
fields of a cell by a 16-bit **field id** (`Data[2:3]`). String fields are transferred two
characters at a time; each 16-bit value `V` packs two 7-bit ASCII characters as
`first = (V >> 7) & 0x7F`, `second = V & 0x7F`.

| Field id      | Field                         | Notes |
| ------------- | ----------------------------- | ----- |
| `0x00`–`0x06` | Description / part string     | up to 14 chars, 2 per id |
| `0x07`–`0x09` | Manufacturer                  | up to 6 chars |
| `0x0A`        | 32-bit value                  | gates the cell-age display; exact meaning TBD |
| `0x0C`        | Install / manufacture date    | packed date (see below); the age is computed from it |
| `0x10`–`0x15` | Serial number (*S/N*)         | up to 12 chars |
| `0x20`–`0xDF` | Calibration-history records   | even ids update the "last cal record" pointer |

The install date at field `0x0C` is a **packed date word** decoded as
`year = (x & 0x7F) + 100`, `month = ((x >> 10) & 0xF) - 1`, `day = (x >> 5) & 0x1F`. The
handset computes **cell age in days** from it, and uses the same epoch as the base timestamp
for calibration records — record *N* is timestamped at `install_date + N * 10800 s` (3-hour
steps). Per-cell status shown on screen: `2` → *"Exp."* (expired), `1` → age in days, `0` →
blank / no data.

# Cell Read Request
ID: `0xD340401` (handset → controller; `dst` = controller device id)

Requests one info field or one calibration record for a cell. `subfn = 2` reads an info field
(ids `0x00`–`0x15`, and the `0x0A`/`0x0C` values); `subfn = 1` reads calibration record *N*.
The controller answers with a [Cell Info Response](#cell-info-response); the handset polls for
that response with a short timeout.

| Byte  | Value                         |
| ----- | ----------------------------- |
| 0     | Cell index (`0`–`2`)          |
| 1     | Subfunction (`2` = field, `1` = record) |
| 2-3   | Field id / record id (big-endian) |

# Cell Info Response
ID: `0xD350004` (controller → handset)

Carries one or two 16-bit values for a field of a cell. `Data[1]` is the count of 16-bit
values in this frame (`1` or `2`, so DLC is 4 or 6; short string requests may be shorter).
`Data[2:3]` is the field id (see [Field ids](#field-ids)); `Data[4:5]` and, when count is 2,
`Data[6:7]` carry the value(s) — two packed 7-bit chars each for string fields, or a raw
16-bit value for numeric/record fields.

| Byte  | Value                            |
| ----- | -------------------------------- |
| 0     | Cell index (`0`–`2`)             |
| 1     | Count of 16-bit values (`1`/`2`) |
| 2-3   | Field id (big-endian)            |
| 4-5   | Value / packed chars (big-endian)|
| 6-7   | Second value (present if count = 2) |

# Cell Record Write
ID: `0xD360401` (handset → controller)

Writes a value into a cell's record store at a record id. The handset uses this to push
computed calibration points (a time word, and `1000 * ppO2 / mV` per cell), then reads the
record back with a [Cell Read Request](#cell-read-request) (`subfn 1`) to verify. Role is a
working theory.

| Byte  | Value                       |
| ----- | --------------------------- |
| 0     | Cell index (`0`–`2`)        |
| 1-2   | Record id (big-endian)      |
| 3-4   | Value (big-endian)          |

# Cell Record Query
ID: `0xD380401` (handset → controller)

A bare one-byte query that starts record enumeration for a cell; the controller replies with a
[Cell Record Ack](#cell-record-ack) carrying the current record cursor.

| Byte  | Value                |
| ----- | -------------------- |
| 0     | Cell index (`0`–`2`) |

# Cell Record Ack
ID: `0xD390004` (controller → handset)

Acknowledges a record request and returns the record cursor. `Data[1:2]` is stored by the
handset as the cell's current record cursor.

| Byte  | Value                       |
| ----- | --------------------------- |
| 0     | Cell index (`0`–`2`)        |
| 1     | Record cursor               |
| 2     | (second cursor byte)        |

# Cell Record Select
ID: `0xD400401` (handset → controller)

Sets a cell's record cursor to a specific record id, observed stepping `0x20`, `0x30`, … in
increments of `0x10` while walking the calibration history. Role is a working theory.

| Byte  | Value                       |
| ----- | --------------------------- |
| 0     | Cell index (`0`–`2`)        |
| 1-2   | Record id (big-endian)      |

# Cell Temperature
ID: `0xD320004` (controller → handset)

Per-cell temperature. This is **distinct** from the `0xC1`
[Temperature](Device%20Metadata.md#temperature) probe message — it is part of this cell-info
sub-protocol and is keyed by cell index. The handset also logs it as an info event.

| Byte  | Value                       |
| ----- | --------------------------- |
| 0     | Cell index (`0`–`2`)        |
| 1-2   | Temperature (big-endian)    |

# Cell Live Value
ID: `0xD330004` (controller → handset)

A per-cell live value; the handset stores it only when it is `>= 100`, which suggests a ppO2
(x1000) or millivolt reading — units TBD. Receiving it also causes the handset to lazily
(re)request the cell's date fields (`0x0A`/`0x0C`) and to re-issue [Bus
Init](Device%20Metadata.md#bus-init) if the cell is not yet known.

| Byte  | Value                       |
| ----- | --------------------------- |
| 0     | Cell index (`0`–`2`)        |
| 1-2   | Value (big-endian)          |

# Assembled cell record

From the responses above the handset maintains one record per cell (three cells) with roughly
these fields, which is what the *O2 Cell* detail screen renders:

| Field           | Source |
| --------------- | ------ |
| Description     | field ids `0x00`–`0x06` (`0x35`) |
| Manufacturer    | field ids `0x07`–`0x09` (`0x35`) |
| Serial (*S/N*)  | field ids `0x10`–`0x15` (`0x35`) |
| Install date    | field `0x0C` (`0x35`), packed date |
| Age (days)      | computed from install date |
| Temperature     | `0x32` |
| Last cal record | even record ids in `0x35` (`0x20`–`0xDF`) |
| Status          | `0` none / `1` show age / `2` *Exp.* |
