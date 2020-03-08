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

class Journal:
    """This class if a simple LIFO array supporting a maximum of size elements.
    """
    def __init__(self, size):
        self.journal = []
        self.size = size

    def append(self, data):
        self.journal.append(data)
        if len(self.journal) > self.size:
            del self.journal[0]

    def array(self):
        return self.journal
