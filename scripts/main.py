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
import socket
import meshreceiver
import utime
import ubinascii
import sireader
from microWebSrv import MicroWebSrv
from uartreader import uartReader
from meshsender import meshsender
from meossender import meossender
from ucollections import deque
from journal import Journal

try:
    from pymesh_config import PymeshConfig
except:
    from _pymesh_config import PymeshConfig

try:
    from pymesh import Pymesh
except:
    from _pymesh import Pymesh

roles = {
#   0x240ac4c77738 : leaf
    b'240ac4c74e5c': "leaf",
#   0x240ac4c781c0 : border router
    b'240ac4c781c0': "border router"
}

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

@MicroWebSrv.route("/sipy/punches", "GET")
def wlanScanHandler(httpClient, httpResponse, routeArgs=None):
    punches = []
    for p in punches_journal.array():
        data = sireader.decode(p)
        punches.append({ 'time': "%02dh%02dm%02ds%003dms" % (data["h"], data["m"], data["s"], data["ms"]),
        'SN': data["SN"],
        'CN': data["CN"] })
    punches.reverse()
    json_punches = ujson.dumps(punches)
    httpResponse.WriteResponseOk( headers		 = None,
								  contentType	 = "application/json",
								  contentCharset = "UTF-8",
								  content 		 = json_punches)

srv = MicroWebSrv(webPath="www/")
srv.SetNotFoundPageUrl("index.html")
srv.Start(threaded=True)

# Launch SRR reader thread
role = roles[ubinascii.hexlify(wl.mac().sta_mac)]

def dummy_cb(rcv_ip, rcv_port, rcv_data):
    #print('Incoming %d bytes from %s (port %d):' % (len(rcv_data), rcv_ip, rcv_port))
    print(rcv_data)
    return

def border_router_loop():
    while True:
        pymesh.br_set(PymeshConfig.BR_PRIORITY_NORM, meshreceiver.siMessageCB)
        utime.sleep(60)

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

if role == "leaf":
    print("This node is a leaf")

    # First create the shared lock

    punches_lock = _thread.allocate_lock()
    # Crate the list of message from UART SRR to PyMesh
    punches = deque((), 200)

    _thread.start_new_thread(uartReader, (punches, punches_journal, punches_lock))
    _thread.start_new_thread(meshsender, (punches, punches_lock, pymesh, meosIp))

elif role == "border router":
    print("This node is the border router")
    # First create the shared lock

    punches_lock = _thread.allocate_lock()
    # Crate the list of message from UART SRR to PyMesh
    punches = deque((), 200)

    # Initialize Pymesh as boder router
    mesh_receiver = meshreceiver.MeshReceiver(punches_journal, punches_lock, punches)
    pymesh.br_set(PymeshConfig.BR_PRIORITY_NORM, mesh_receiver.siMessageCB)

    # Initialize TCP/IP relay
    _thread.start_new_thread(meossender, (punches, punches_lock, "SERVER", 10000))
