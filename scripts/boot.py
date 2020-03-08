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

# boot.py -- run on boot-up

import network
import pycom
from machine import RTC

pycom.heartbeat(False)
pycom.rgbled(0x000800)
wl = network.WLAN()
wl.init(mode = network.WLAN.STA)
wl.connect("Nounette", auth = (network.WLAN.WPA2, "~vHff4uvJ}*C(7(n"))
while not wl.isconnected():
    pass
# synchronize RTC
rtc = RTC()
rtc.ntp_sync("pool.ntp.org")
# Initialization fininshed
pycom.rgbled(0)
print(wl.ifconfig()[0]+"/"+wl.ifconfig()[1])
