import connectedrace
import can

testmessage = can.Message(data=[1,2,3,4,5,6,7,8])
node = connectedrace.Node('127.0.0.1', testmessage)

class NodeTest:
    def test_one(self):
        assert isinstance(self.last_msg, can.Message)
        assert self.ip == '127.0.0.1'
        assert isinstance(self.timestamp, float)
