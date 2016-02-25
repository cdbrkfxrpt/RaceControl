import can
from connectedrace.antenna import *

testmessage = can.Message(data=[1,2,3,4,5,6,7,8])
node = Node('127.0.0.1', testmessage)
listener = can.BufferedReader()
daemon = AntennaDaemon(listeners=[listener])

def test_node():
    assert isinstance(node.last_msg, can.Message)
    assert node.ip == '127.0.0.1'
    assert isinstance(node.timestamp, float)

class AntennaDaemonTests:
    def test_init(self):
        assert daemon.ip == socket.gethostbyname(socket.getfqdn())
        assert daemon.tcpport == S_PORT
        assert daemon.udpport == D_PORT
        assert listener in daemon.listeners
        assert not daemon.nodes
        assert isinstance(daemon.Cannon, Cannon)
        assert daemon.running

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
        new_node = Node('localhost')
        daemon.add_node(new_node)
        assert new_node in daemon.nodes

    def test_ip_list(self):
        assert '127.0.0.1' in daemon.ip_list()
        assert 'localhost' in daemon.ip_list()

    def test_check_nodes(self):
        node.timestamp += 10
        daemon.check_nodes()
        assert node not in daemon.nodes
