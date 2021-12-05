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
import usocket
import ubinascii
import sipypacket

# TCP packet expected by MeOS
#
# struct SIOnlinePunch {
#  BYTE Type;  //0=punch, 255=Triggered time
#  WORD CodeNo;  //2 byte 0-65K (station code)
#  DWORD SICardNo; //4 byte integer  -2GB until +2GB
#  DWORD CodeDay; //Obsolete, not used anymore
#  DWORD CodeTime;  //Time
# };


def meossender(punches, punches_lock, config):
    while True:
        punches_lock.acquire(1)
        # Messages are available
        if len(punches) > 0:
            # Send message over TCP/IP to MeOs server
            # Now you can use that address
            meos_packet = bytearray()
            while len(punches) > 0:
                punch = punches.popleft()
                # MeOS packet of punch type (O)
                meos_packet.append(0)

                # Station number
                meos_packet.append(punch[sipypacket.CN0])
                meos_packet.append(punch[sipypacket.CN1])

                # SIcard number
                meos_packet.append(punch[sipypacket.SN0])
                meos_packet.append(punch[sipypacket.SN1])
                meos_packet.append(punch[sipypacket.SN2])
                meos_packet.append(punch[sipypacket.SN3])

                # Day (obsolete)
                meos_packet.append(0)
                meos_packet.append(0)
                meos_packet.append(0)
                meos_packet.append(0)

                # Time (in 1/10s)
                meos_packet.append(punch[sipypacket.TM0])
                meos_packet.append(punch[sipypacket.TM1])
                meos_packet.append(punch[sipypacket.TM2])
                meos_packet.append(punch[sipypacket.TM3])

            retry = True
            while retry:
                try:
                    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
                    addr = usocket.getaddrinfo(config.get(
                        'meos')['address'], config.get('meos')['port'])[0][-1]
                    sock.settimeout(5)
                    sock.connect(addr)
                    sock.sendall(meos_packet)
                    sock.close()
                except OSError as msg:
                    print("[%02dh%02dm%02ds]" % utime.localtime()[3:6],
                          "- meossender -", "OS error: {0}".format(msg))
                else:
                    print("[%02dh%02dm%02ds]" % utime.localtime()[3:6],
                          "- meossender -", ubinascii.hexlify(meos_packet))
                    retry = False
