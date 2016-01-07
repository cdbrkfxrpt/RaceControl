import can

class Daemon(object):
    def __init__(self, interface='vcan0', listeners=None):
        self.bus = can.interface.Bus(interface, bustype='socketcan_native')

        self.listeners = []
        if listeners is not None:
            for l in listeners:
                if isinstance(l, can.Listener):
                    self.listeners.append(l)

    def add_listener(self, listener):
        if isinstance(listener, can.Listener):
            self.listeners.append(listener)

    def run(self, timeout=None):
        can.Notifier(self.bus, self.listeners, timeout)

    def __call__(self, msg):
        pass
