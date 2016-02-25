import socket, socketserver
import time
import pickle
from connectedrace.globals import D_PORT, PROTOCOL

class BucketHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        node_msg = self.rfile.read().strip()
        ip_list = self.server.antennad.ip_list()
        if self.client_address[0] in ip_list:
            timestamp = time.perf_counter()
            for node in self.server.antennad.nodes:
                if node.ip == self.client_address[0]:
                    node.timestamp = timestamp

            node_msg = node_msg.split(b'#')
            node_msg = list(msg for msg in node_msg
                               if msg and not msg in PROTOCOL)
            for msg in node_msg:
                try:
                    self.server.antennad.notify(pickle.loads(msg))
                except (pickle.UnpicklingError, EOFError):
                    # syslog.write('corrupted data')
                    print('corrupted data received')
                # print('Received message ', msg)

        elif (node_msg == PROTOCOL[0]
            and not self.client_address[0] == self.server.antennad.ip
            and not self.client_address[0] == '127.0.0.1'):
            self.server.antennad.add_node(self.client_address[0], node_msg)
            print('UDP/Node acknowledged: ', self.client_address[0])
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(PROTOCOL[1], (self.client_address[0], D_PORT))
        elif (node_msg == PROTOCOL[1]
            and not self.client_address[0] == self.server.antennad.ip_list
            and not self.client_address[0] == '127.0.0.1'):
            self.server.antennad.add_node(self.client_address[0], node_msg)
            print('UDP/Node registered: ', self.client_address[0])

class Bucket(socketserver.UDPServer):
    def __init__(self, server_address, BucketHandlerClass, antennad):
        super().__init__(server_address, BucketHandlerClass)
        self.antennad = antennad
