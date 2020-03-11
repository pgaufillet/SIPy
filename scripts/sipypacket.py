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

# Index of SIPy packet fields
# Station number
CN0  = 0
CN1  = 1
# SIcard number
SN0  = 2
SN1  = 3
SN2  = 4
SN3  = 5
# Time (in 1/10s)
TM0  = 6
TM1  = 7
TM2  = 8
TM3  = 9

def decode(buf):
    """Decode the frame and store it into a dictionary."""
    data = {}

    # Station Id
    data["SN"] = buf[SN0] + (buf[SN1] << 8) + (buf[SN2] << 16) + (buf[SN3] << 24)

    # Card Id
    data["CN"] = buf[CN0] + (buf[CN1] << 8)

    # Punch Time

    # Time in 1/10s over 32 bits
    timer = (buf[TM3] << 24) + (buf[TM2] << 16) + (buf[TM1] << 8) + buf[TM0]
    data["h"] = timer // 36000
    timer = timer % 36000
    data["m"] = timer // 600
    timer = timer % 600
    data["s"] = timer // 10
    timer = timer % 10
    data["ms"] = timer * 100

    return data
