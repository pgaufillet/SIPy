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
import sireader as si
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
            # Fill the message stack for PyMesh sender
            punches.append(buf)
            punches_journal.append(buf)
            print("[%02dh%02dm%02ds]" % utime.localtime()[3:6], "- uartReader -", ubinascii.hexlify(buf))
        # Now that the UART stream has no more complete messages, raise a mutex
        # to signal meshsender that it has to send them to the border router
        if punches_lock.locked():
            punches_lock.release()
