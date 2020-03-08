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
