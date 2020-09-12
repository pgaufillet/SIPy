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
import network
import utime

def wlanmanager(config):
    wl = network.WLAN()
    if config.has("owned wifi"):
        print('wlanmanager - Setting up WLAN ' + config.get("owned wifi")["ssid"] + "-" + config.get("name"))
        wl.init(mode = network.WLAN.STA_AP,
            ssid = config.get("owned wifi")["ssid"] + "-" + config.get("name"),
            auth = (network.WLAN.WPA2, config.get("owned wifi")["password"]))
        utime.sleep(15)
    else:
        wl.init(mode = network.WLAN.STA)
    while True:
        try:
            if not wl.isconnected():
                wlans = wl.scan()
                wnames = []
                for w in wlans:
                    wnames.append(w.ssid)
                selected_wifi = None
                for kw in config.get("known wifi"):
                    if kw['ssid'] in wnames:
                        selected_wifi = kw
                        break
                if selected_wifi != None:
                    print("wlanmanager - Connecting to " + selected_wifi['ssid'])
                    wl.connect(selected_wifi['ssid'], auth = (selected_wifi['auth'], selected_wifi['password']))
        except:
            print("wlanmanager - Failure")
        utime.sleep(60)
