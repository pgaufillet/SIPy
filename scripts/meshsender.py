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
import ubinascii

def meshsender(punches, punches_lock, pymesh, meosIp):
    while True:
        punches_lock.acquire(1)
        # Messages are available
        while len(punches) > 0:
            punch = punches.popleft()
            # Send message over PyMesh
            print("[%02dh%02dm%02ds]" % utime.localtime()[3:6], "- meshsender -", ubinascii.hexlify(punch))
            pymesh.send_mess_external(meosIp, 10000, punch)
            # Work around utime.sleep(x) bug which sleeps for 1s whatever
            # the value of x is
            for i in range(10):
                utime.sleep(1)
