from connectedrace.cannon import *
from connectedrace.antenna import AntennaDaemon

antennad = AntennaDaemon(5255, 5256)
cannon = Cannon(antennad)

class TestCannon:
    def test_init(self):
        assert isinstance(cannon.buffer, can.BufferedReader)
        assert cannon.antennad == antennad
        assert cannon.port == D_PORT
        assert cannon.sock.type == socket.socket(socket.AF_INET, socket.SOCK_DGRAM).type
        assert cannon.timeout == 100
        assert cannon.projectile == b''
        assert isinstance(cannon.trigger, float)
        assert cannon.running.is_set()

    def test_fire(self):
        cannon.projectile = b'asdf'
        cannon.fire(cannon.projectile)
        assert cannon.projectile == b''
        assert isinstance(cannon.trigger, float)
