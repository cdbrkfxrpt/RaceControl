# RaceControl, a bidirectional CAN bus telemetry platform.
# Copyright (C) 2016 Florian Eich

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import threading
import can

from racecontrol.globals import CAN_IFACE


class CANCom:
    """CANCom class for establishing the CAN bus connection and
    sending/receiving on it.

    The CANCom class, when instantiated, establishes the CAN bus connection and
    starts a thread to transmit CAN data received from other application
    sources. It also instantiates a can.Notifier object which is itself a
    threaded listener on the CAN bus and connects it to the listeners it knows.
    """
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
        """
        Method to add a listener to a CANCom object. All listeners in a CANCom
        object are notified when a message is read from the bus.
        """
        self.stop_notifier()
        if isinstance(listener, can.Listener):
            self.listeners.append(listener)
        else:
            raise TypeError('Only can.Listeners allowed.')
        self.notifier = self.run_notifier()

    def run_notifier(self, timeout=None):
        """
        Method to create a new Notifier on the CANCom object's bus. Returns an
        instantiated can.Notifier object. Used to create a new notifier object
        whenever a listener is added.
        """
        return can.Notifier(self.bus, self.listeners, timeout)

    def stop_notifier(self):
        """
        Method to stop the current notifier. Used whenever a listener is added
        to stop the old notifier so the thread won't become zombied in the
        interpreter.
        """
        self.notifier.running.clear()

    def operate(self):
        """
        Method which is the target of the thread. It listens to the object's
        message buffer for messages from the other application members and, if
        there is a message, sends it to the CAN bus after filtering it with the
        blacklist.
        """
        while self.running.is_set():
            msg = self.buffer.get_message(0)
            if (isinstance(msg, can.Message) and
               msg.arbitration_id not in self.blacklist):
                print('Sending to CAN ', msg)
                self.bus.send(msg)
