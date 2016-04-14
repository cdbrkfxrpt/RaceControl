import sys
import threading
import can
from globals import CAN_IFACE


class CableDaemon:
    def __init__(self, interface=CAN_IFACE, listeners=[], timeout=None):
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

        self.timeout = timeout

        self.buffer = can.BufferedReader()

        self.notifier = self.run_notifier(self.timeout)

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
        self.notifier = self.run_notifier(self.timeout)

    def run_notifier(self, timeout=None):
        return can.Notifier(self.bus, self.listeners, timeout)

    def stop_notifier(self):
        self.notifier.running.clear()

    def operate(self):
        while self.running.is_set():
            msg = self.buffer.get_message(0)
            if isinstance(msg, can.Message):
                # print('Sending to CAN ', msg)
                self.bus.send(msg)
