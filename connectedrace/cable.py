import can
import queue

class CableDaemon(object):
    def __init__(self, interface='vcan0', listeners=[], timeout=30):
        self.bus = can.interface.Bus(interface, bustype='socketcan_native')

        self.listeners = []
        for l in listeners:
            if isinstance(l, can.Listener):
                self.listeners.append(l)
            else:
                raise TypeError('Only can.Listeners allowed.')

        self.timeout = timeout

        self.notifier = self.run(self.timeout)

    def add_listener(self, listener):
        self.stop()
        if isinstance(listener, can.Listener):
            self.listeners.append(listener)
        else:
            raise TypeError('Only can.Listeners allowed.')
        self.run(self.timeout)

    def run(self, timeout=None):
        return can.Notifier(self.bus, self.listeners, timeout)

    def stop(self):
        self.notifier.running.clear()

    def on_call_execute(self, msgqueue):
        while not msgqueue.empty():
            self.bus.send(msgqueue.get_nowait())

    def __call__(self, msglist=[]):
        if msglist is not None:
            self.on_call_execute(msglist)
