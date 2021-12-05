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
