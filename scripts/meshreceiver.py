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


class MeshReceiver:
    def __init__(self, journal, lock, punches):
        self.journal = journal
        self.lock = lock
        self.punches = punches

    def siMessageCB(self, rcv_ip, rcv_port, rcv_data, dest_ip, dest_port):
        print("[%02dh%02dm%02ds]" % utime.localtime()[3:6],
              "- meshreceiver -", ubinascii.hexlify(rcv_data))
        self.journal.append(rcv_data)
        self.punches.append(rcv_data)
        self.lock.release()
        return
