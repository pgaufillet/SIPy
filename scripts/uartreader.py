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

import utime
import sireader
import ubinascii
from machine import UART

# Initializes UART for SI SRR OEM module
uart = UART(1, baudrate=38400)


def uartReader(punches, punches_journal, punches_lock):
    while True:
        # Sleep for 1s (other values don't work in a thread anyway)
        utime.sleep(1)
        while uart.any() >= 20:
            buf = uart.read(20)
            sipy_packet = bytearray()
            # Station number
            sipy_packet.append(buf[sireader.CN0])
            sipy_packet.append(buf[sireader.CN1])

            # SIcard number
            sipy_packet.append(buf[sireader.SN0])
            sipy_packet.append(buf[sireader.SN1])
            sipy_packet.append(buf[sireader.SN2])
            sipy_packet.append(buf[sireader.SN3])

            # Time (in 1/10s)
            time = int(((10 * buf[sireader.TSS]) >> 8) + 10
                       * (buf[sireader.TL] + (buf[sireader.TH] << 8)
                          + ((buf[sireader.TD] & 0b00000001) * 43200)))
            sipy_packet.append(time & 0xff)
            sipy_packet.append((time >> 8) & 0xff)
            sipy_packet.append((time >> 16) & 0xff)
            sipy_packet.append((time >> 24) & 0xff)

            # Fill the message stack for PyMesh sender
            punches.append(sipy_packet)
            punches_journal.append(sipy_packet)
            print("[%02dh%02dm%02ds]" % utime.localtime()[3:6],
                  "- uartReader -", ubinascii.hexlify(sipy_packet))
        # Now that the UART stream has no more complete messages, raise a mutex
        # to signal meshsender that it has to send them to the border router
        if punches_lock.locked():
            punches_lock.release()
