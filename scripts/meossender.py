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
import sireader

# TCP packet expected by MeOS
#
#struct SIOnlinePunch {
#  BYTE Type;  //0=punch, 255=Triggered time
#  WORD CodeNo;  //2 byte 0-65K (station code)
#  DWORD SICardNo; //4 byte integer  -2GB until +2GB
#  DWORD CodeDay; //Obsolete, not used anymore
#  DWORD CodeTime;  //Time
#};

def meossender(punches, punches_lock, meosServer, meosPort):
    while True:
        punches_lock.acquire(1)
        # Messages are available
        if len(punches) > 0:
            sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
            addr = usocket.getaddrinfo(meosServer, meosPort)[0][-1]
            sock.connect(addr)
            while len(punches) > 0:
                punch = punches.popleft()
                # Send message over TCP/IP to MeOs server
                # Now you can use that address
                meos_packet = bytearray()
                # MeOS packet of punch type (O)
                meos_packet.append(0)

                # Station number
                meos_packet.append(punch[sireader.CN0])
                meos_packet.append(punch[sireader.CN1])

                # SIcard number
                meos_packet.append(punch[sireader.SN0])
                meos_packet.append(punch[sireader.SN1])
                meos_packet.append(punch[sireader.SN2])
                meos_packet.append(punch[sireader.SN3])

                # Day (obsolete)
                meos_packet.append(0)
                meos_packet.append(0)
                meos_packet.append(0)
                meos_packet.append(0)

                # Time (in 1/10s)
                time = int(((10 * punch[sireader.TSS]) >> 8) + 10 *
                    (punch[sireader.TL] + (punch[sireader.TH] << 8) +
                    ((punch[sireader.TD] & 0b00000001) * 43200)))
                meos_packet.append(time & 0xff)
                meos_packet.append((time >> 8) & 0xff)
                meos_packet.append((time >> 16) & 0xff)
                meos_packet.append((time >> 24) & 0xff)

                print("[%02dh%02dm%02ds]" % utime.localtime()[3:6], "- meossender -", ubinascii.hexlify(meos_packet))
                sock.sendall(meos_packet)
            sock.close()
