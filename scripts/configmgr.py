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

import ujson


class ConfigMgr:
    def __init__(self, default = {}):
        self.load(default = default)

    def reset(self, default = {}):
        self.config = default.copy()
        self.save()

    def set(self, key, value):
        self.config[key] = value

    def unset(self, key):
        self.config.pop(key)

    def get(self, key):
        return self.config[key]

    def has(self, key):
        return key in self.config

    def load(self, default = {}):
        try:
            with open('config.json') as f:
                self.config = ujson.load(f)
        except OSError:
            self.config = default
            self.save()

    def save(self):
        with open('config.json', 'w') as f:
            ujson.dump(self.config, f)
