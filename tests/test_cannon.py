import pytest
from connectedrace.cannon import *
from connectedrace.antenna import AntennaDaemon

class TestCannon:
    def test_init(self, cannon, antenna):
        assert isinstance(cannon.buffer, can.BufferedReader)
        assert cannon.antennad == antenna
        assert cannon.port == D_PORT
        assert cannon.sock.type == socket.socket(socket.AF_INET, socket.SOCK_DGRAM).type
        assert cannon.timeout == 100
        assert cannon.projectile == b''
        assert isinstance(cannon.trigger, float)
        assert cannon.running.is_set()

    def test_fire(self, cannon):
        cannon.projectile = b'asdf'
        cannon.fire(cannon.projectile)
        assert cannon.projectile == b''
        assert isinstance(cannon.trigger, float)
