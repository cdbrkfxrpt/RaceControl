import pytest
from connectedrace.antenna import *

class TestNode():
    def test_node(self, message, node):
        assert node.last_msg == message
        assert node.ip == '127.0.0.1'
        assert isinstance(node.timestamp, float)


class TestAntenna:
    def test_init(self, listener, antenna):
        assert antenna.ip == socket.gethostbyname(socket.getfqdn())
        assert antenna.tcpport == S_PORT
        assert antenna.udpport == D_PORT
        assert listener in antenna.listeners
        assert not antenna.nodes
        assert isinstance(antenna.cannon, Cannon)
        assert antenna.running.is_set()


    def test_add_listener(self, antenna):
        new_listener = can.Printer()

        antenna.add_listener(new_listener)
        assert new_listener in antenna.listeners

        antenna.listeners.remove(new_listener)
        assert new_listener not in antenna.listeners

        with pytest.raises(TypeError):
            antenna.add_listener('blubb')


    def test_notify(self, message, listener, antenna):
        antenna.notify(message)
        assert listener.get_message() == message


    def test_add_node(self, message, antenna):
        antenna.add_node('127.0.0.1', message)
        assert antenna.nodes[0].ip == '127.0.0.1'

        antenna.nodes = []
        assert not antenna.nodes


    def test_ip_list(self, antenna):
        antenna.add_node('127.0.0.1')
        assert '127.0.0.1' in antenna.ip_list()

        antenna.nodes = []
        assert '127.0.0.1' not in antenna.ip_list()
