#    SIPy - Meshed LoRa network for SportIdent SRR Orienteering stations
#           based on Pycom LoPy4
#    Copyright (C) 2020  Pierre GAUFILLET
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Decode SI Data record transmission frames

"""This class provides helpers to encode/decode Data Record Transmission
frames used for SRR punches."""
# SI Protocol tags
STX                       = b'\x02'
ETX                       = b'\x03'
DLE                       = b'\x10'
NAK                       = b'\x15'
WAKEUP                    = b'\xFF'

# Data record transmission used as command code for SRR punch read
DATA_RECORD_TRANSMISSION  = b'\xD3'

# Index of bytes in Data record transmission frames (20 bytes including the
# 0xFF header)
LEN  = 3
CN1  = 4
CN0  = 5
SN3  = 6
SN2  = 7
SN1  = 8
SN0  = 9
TD   = 10
TH   = 11
TL   = 12
TSS  = 13
MEM2 = 14
MEM1 = 15
MEM0 = 16
CRC1 = 17
CRC0 = 18


def decode(buf):
    """Decode the frame and store it into a dictionary."""
    data = {}

    # Station Id
    data["SN"] = buf[SN0] + (buf[SN1] << 8) + (buf[SN2] << 16) + (buf[SN3] << 24)

    # Card Id
    data["CN"] = buf[CN0] + (buf[CN1] << 8)

    # Punch Time
    data["day"] = (buf[TD] & 0b00001110) >> 1
    # Add 12h*3600=43200 if TD bit 0 (am=0/pm=1) is set
    timer = int(buf[TL] + (buf[TH] << 8) + ((buf[TD] & 0b00000001) * 43200))
    data["h"] = timer // 3600
    timer = timer % 3600
    data["m"] = timer // 60
    data["s"] = timer % 60
    data["ms"] = int(1000 * (buf[TSS] / 256))

    # Station memory index
    data["mem"] = buf[MEM0] + (buf[MEM1] << 8) + (buf[MEM2] << 16)
    return data
