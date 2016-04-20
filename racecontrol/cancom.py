# RaceControl, a bidirectional CAN bus telemetry platform.
# Copyright (C) 2016 Florian Eich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import threading
import can

from racecontrol.globals import CAN_IFACE


class CANCom:
    def __init__(self, blacklist, interface=CAN_IFACE, listeners=[]):
        self.blacklist = blacklist

        try:
            self.bus = can.interface.Bus(interface, bustype='socketcan_native')
            self.interface = interface
            print('Connected to CAN interface ', self.interface)
        except OSError:
            print('No CAN interface defined/interface not found.')
            sys.exit(1)

        self.listeners = []
        for listener in listeners:
            if isinstance(listener, can.Listener):
                self.listeners.append(listener)
            else:
                raise TypeError('Only can.Listeners allowed.')

        self.buffer = can.BufferedReader()

        self.notifier = self.run_notifier()

        self.running = threading.Event()
        self.running.set()

        self._transmit = threading.Thread(target=self.operate)
        self._transmit.daemon = True

        self._transmit.start()

    def add_listener(self, listener):
        self.stop_notifier()
        if isinstance(listener, can.Listener):
            self.listeners.append(listener)
        else:
            raise TypeError('Only can.Listeners allowed.')
        self.notifier = self.run_notifier()

    def run_notifier(self, timeout=None):
        return can.Notifier(self.bus, self.listeners, timeout)

    def stop_notifier(self):
        self.notifier.running.clear()

    def operate(self):
        while self.running.is_set():
            msg = self.buffer.get_message(0)
            if (isinstance(msg, can.Message) and
               msg.arbitration_id not in self.blacklist):
                # print('Sending to CAN ', msg)
                self.bus.send(msg)
