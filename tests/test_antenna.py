import connectedrace
import can

testmessage = can.Message(data=[1,2,3,4,5,6,7,8])

class NodeTest:
    def __init__(self):
        node = Node('127.0.0.1', testmessage)

    def test_one(self):
        assert self.last_msg.isinstance(can.Message)
        assert self.ip == '127.0.0.1'
        assert self.timestamp
