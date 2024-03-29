SIPy
----
SIPy is a project of meshed LoRa network for SportIdent SRR orienteering stations based on Pycom LoPy4.

The communication path is:

**SI BSF8-SRR** --SRR--> **SI SRR module** --UART--> **LoPy4** --PyMesh--> **LoPy4** --WiFi+TCP--> **MeOS**.

# Hardware
* SportIdent SRR BSF8-SRR-DB and SRR modules: <https://www.sportident.com> and <https://www.sportident.com/images/PDF/1_si_base_products/8_si-radio/SRR-Kit/SPORTident_SRR_en.pdf>.
* Pycom LoPy4: <https://pycom.io/product/lopy4/>.
* Pycom expansion <https://pycom.io/product/expansion-board-3-0/>.

# Software
* MeOS: <http://www.melin.nu/meos/en/> and <https://github.com/melinsoftware/meos>.
* Pycom documentation: <https://docs.pycom.io>.

Configuration guide
----------------
SiPy requires some configuration before being used. These configurations for
now can be done only by using the applicative configuration API or directly by
editing the file `config.json`. Using REPL:
```
config.set("name",<node name>)
config.set("role","border router" | "leaf")
config.save()
```
It changes the name configuring the owned WLAN SSID to GEC-<node name> by default.
The border router, in Pymesh terminology, is a node bridging to another network.
In the case of SiPy, only one node shall be set up, bridging the LoRa mesh and
the IPv4 network used by GEC computers.

A SiPy node provides 2 simultaneous Wifi modes:
* As an Access Point, configured as the `owned wifi`
* As a client, configured as the `known wifi` (several wlans can be configured).

The owned wlan is very handy for accessing the administration web page of a node,
while the known wlans are rather used as bridges between LoRa mesh and GEC network.
Nevertheless, both kind of wlans can be used undifferently for both purposes.

Node administration
-------------------
The admnistration web pages can be accessed once on the same network that the node,
with any web browser at [http://\<node ip address\>]().

Architecture
------------

SIPy nodes can be of 2 types:
* __Leaf__: general case. Leaf nodes read punches and send them to the router.
* __router__: only one router in the network, receiving punches from leaf and
relaying them to MeOS.

Leafs and router nevertheless share the same software. During the boot, different
parts are activated depending on the local configuration:
* on the leafs, the thread __uartReader__ in charge of the link to the SportIdent radio is started.
It decodes the message and assemble a SIPy LoRa packet. Then it stores it in a
stack and it signals it using __punches_lock__ to the thread __meshsender__ in charge of LoRa emission.
* on the router, the thread __mesh_receiver.siMessageCB__ is in charge of receiving the LoRa messages. It decodes
it and assemble a SportIdent packet. It then signals it using __punches_lock__ to the thread __meossender__ in
charge of WLAN messages. This last thread opens a UDP socket to MeOS and send
the punch packet.

2 more threads run on all nodes:
* a thread in charge of WLAN management: it scans continuously the local WLAN,
and connect to it if it matches the __known wifi__ configuration parameter. If
not, the node switches to WLAN Access Point mode and broadcasts it.
* a thread in charge of the HTTP management: this web access is solely used
for diagnostic and administration purposes.

Technical notes
---------------
* Never, __NEVER__ start a Pycom module without its LoRa antenna: there are good
chances to burn out the radio amplifier.

* LoRa transmitter/receiver couple is very sensible. A minimum distance of about
1m is required to about errors of transmission.

* LoRa mesh LED color codes:
 * __Red__: not connected / searching
 * __Cyan__: single leader node (no other node on the mesh)
 * __White__: child (leaf)
 * __Green__: router node
 * __Magenta__: leader node
 * __Blinking__: sending/receiving packets

 In normal operations, only one node shall be magenta, all the other are green or
 white, depending on the number of nodes.

 This behaviour can be disabled as described by Catalin in the Pycom forum
 <https://forum.pycom.io/topic/6337/pymesh-and-rgb-led/3>:
 ```
 For now, the solution is to comment-out this line: https://github.com/pycom/pycom-libraries/blob/1df042c6faf032d40c48a647cb6d158d94304d23/pymesh/pymesh_frozen/lib/mesh_internal.py#L265
Basically, the method led_state controls the LED.
So, you should take the file mesh_internal.py modify it (comment out that line) and upload it on the device. This module/file will be used, as it has higher priority than the one included in the frozen, as binary.
Let me know how it goes.
```

* From Pycom 1.20.2r2+, Pymesh can only be provisioned from Pybytes (<https://pybytes.pycom.io>).
Once provisioned, the way Pymesh is configured is altered and the board uses Pybytes data.
To avoid this behaviour, the following instructions can be used to disable Pybytes
on a given LoPy4 board:

```
import pycom
pycom.pybytes_on_boot(False)
machine.reset()
```

It can be reverted with the same commands replacing `False` by `True`.
