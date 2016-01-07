import can

class CableDaemon(object):
    def __init__(self, interface='vcan0', listeners=[], timeout=30):
        self.bus = can.interface.Bus(interface, bustype='socketcan_native')

        self.listeners = listeners
        for l in listeners:
            if isinstance(l, can.Listener):
                self.listeners.append(l)

        self.timeout = timeout

        self.notifier = self.run(self.timeout)

    def add_listener(self, listener):
        self.stop()
        if isinstance(listener, can.Listener):
            self.listeners.append(listener)
        self.run(self.timeout)

    def run(self, timeout=None):
        return can.Notifier(self.bus, self.listeners, timeout)

    def stop(self):
        self.notifier.running.clear()

    def on_call_execute(self, msglist=[]):
        for msg in msglist:
            self.bus.send(msg)

    def __call__(self, msglist=[]):
        if msglist is not None:
            self.on_call_execute(msglist)
