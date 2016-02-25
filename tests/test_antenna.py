import pytest
from connectedrace.antenna import *

testmessage = can.Message(data=[1,2,3,4,5,6,7,8])
node = Node('127.0.0.1', testmessage)
listener = can.BufferedReader()
daemon = AntennaDaemon(listeners=[listener], node_ips=[])

class TestNode():
    def test_node(self):
        assert node.last_msg == testmessage
        assert node.ip == '127.0.0.1'
        assert isinstance(node.timestamp, float)

class TestAntenna:
    def test_init(self):
        assert daemon.ip == socket.gethostbyname(socket.getfqdn())
        assert daemon.tcpport == S_PORT
        assert daemon.udpport == D_PORT
        assert listener in daemon.listeners
        assert not daemon.nodes
        assert isinstance(daemon.cannon, Cannon)
        assert daemon.running.is_set()

    def test_add_listener(self):
        new_listener = can.Printer()
        daemon.add_listener(new_listener)
        assert new_listener in daemon.listeners
        with pytest.raises(TypeError):
            daemon.add_listener('blubb')

    def test_notify(self):
        daemon.notify(testmessage)
        assert listener.get_message() == testmessage

    def test_add_node(self):
        daemon.add_node('127.0.0.1', testmessage)
        assert daemon.nodes[0].ip == '127.0.0.1'

    def test_ip_list(self):
        assert '127.0.0.1' in daemon.ip_list()
