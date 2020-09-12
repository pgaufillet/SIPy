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
import ujson
import _thread
import meshreceiver
import utime
import sipypacket
from wlanmanager import wlanmanager
from microWebSrv import MicroWebSrv
from uartreader import uartReader
from meshsender import meshsender
from meossender import meossender
from ucollections import deque
from journal import Journal
from configmgr import ConfigMgr

try:
    from pymesh_config import PymeshConfig
except:
    from _pymesh_config import PymeshConfig

try:
    from pymesh import Pymesh
except:
    from _pymesh import Pymesh

# Use only one char for name (preferably A-Z to avoid confusion with SI controls).
default_config = {
                    "name": "A",
                    "role": "leaf",
                    "known wifi": [
                                    {
                                        "ssid": "STA_SSID",
                                        "auth": network.WLAN.WPA2,
                                        "password": "PASSWORD"
                                    }
                    ],
                    "owned wifi": {
                        "ssid": "GEC",
                        "auth mode": network.WLAN.WPA2,
                        "password": "PASSWORD"
                    },
                    "meos": {
                    "address": "192.168.4.2",
                    "port": "10000"
                    }
                 }

config = ConfigMgr(default = default_config)

# Configure Wifi - a local AP for stand alone mode using config parameters
# Optionally connect as STA to a known WiFi
_thread.start_new_thread(wlanmanager, (config,))

meosIp = "2020::1"
punches_journal = Journal(10)

@MicroWebSrv.route("/wlan/scan", "GET")
def wlanScanHandler(httpClient, httpResponse, routeArgs=None):
    wl = network.WLAN()
    wlans = []
    for w in wl.scan():
        wlans.append({ 'ssid': w.ssid, 'channel': w.channel, 'rssi': w.rssi })
    wlans = ujson.dumps(wlans)
    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "application/json",
								  contentCharset = "UTF-8",
								  content 		 = wlans)

@MicroWebSrv.route("/pymesh/monitor", "GET")
def pymeshHandler(httpClient, httpResponse, routeArgs=None):
    pn = pymesh.mesh.mesh.mesh.mesh.neighbors()
    neighbours = [{ 'mac': pymesh.mac(), 'rssi': 0 }]
    for node in pn:
        neighbours.append({ 'mac': node.mac, 'rssi': node.rssi })
    neighbours = ujson.dumps(neighbours)
    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "application/json",
								  contentCharset = "UTF-8",
								  content 		 = neighbours)

@MicroWebSrv.route("/sipy/punches", "GET")
def punchesHandler(httpClient, httpResponse, routeArgs=None):
    punches = []
    for p in punches_journal.array():
        data = sipypacket.decode(p)
        punches.append({ 'time': "%02dh%02dm%02ds%003dms" % (data["h"], data["m"], data["s"], data["ms"]),
            'SN': data["SN"],
            'CN': data["CN"] })
    punches.reverse()
    json_punches = ujson.dumps(punches)
    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "application/json",
								  contentCharset = "UTF-8",
								  content 		 = json_punches)

def dummy_cb(rcv_ip, rcv_port, rcv_data):
    #print('Incoming %d bytes from %s (port %d):' % (len(rcv_data), rcv_ip, rcv_port))
    print(rcv_data)
    return

# Initialize Pymesh as leaf

# LoRa config for France 500mW on band 54 (869,4-869,65MHz)
# {
#   "debug": 5,
#   "LoRa": {
#     "sf": 7,
#     "region": LoRa.EU868,
#     "freq": 869500000,
#     "bandwidth": LoRa.BW_500KHZ
#     },
#   "Pymesh": {"key": "50421ef968433195d49784d96f3bbb5b"}
# }
pymesh_config = PymeshConfig.read_config()
pymesh = Pymesh(pymesh_config, dummy_cb)

# Wait until pymesh is up
while not pymesh.is_connected():
    utime.sleep(1)

if config.get('role') == "leaf":
    print("main - Starting as a leaf")

    # First create the shared lock

    punches_lock = _thread.allocate_lock()
    # Crate the list of message from UART SRR to PyMesh
    punches = deque((), 200)

    _thread.start_new_thread(uartReader, (punches, punches_journal, punches_lock))
    _thread.start_new_thread(meshsender, (punches, punches_lock, pymesh, meosIp))

elif config.get('role') == "border router":
    print("main - Starting as border router")
    # First create the shared lock

    punches_lock = _thread.allocate_lock()
    # Crate the list of message from UART SRR to PyMesh
    punches = deque((), 200)

    # Initialize Pymesh as boder router
    mesh_receiver = meshreceiver.MeshReceiver(punches_journal, punches_lock, punches)
    pymesh.br_set(PymeshConfig.BR_PRIORITY_NORM, mesh_receiver.siMessageCB)

    # Initialize TCP/IP relay
    _thread.start_new_thread(meossender, (punches, punches_lock, config))

srv = MicroWebSrv(webPath="www/")
srv.SetNotFoundPageUrl("index.html")
srv.Start(threaded=True)
