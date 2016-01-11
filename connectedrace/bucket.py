import socket, socketserver
import pickle

class BucketHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        print('life sign from BucketHandler')
        if self.client_address in self.server.antennad.nodes:
            msglist = rfile.read().split(b'#')
            msglist = list(msg for msg in msglist
                               if msg and not msg in PROTOCOL)
            for msg in msglist:
                try:
                    self.server.antennad.notify(pickle.loads(msg))
                except pickle.UnpicklingError:
                    # syslog.write('corrupted data')
                    print('corrupted data received')
                print('Received message ', msg)
        elif rfile.readline().strip() == PROTOCOL[0]:
            self.server.antennad.add_node(self.client_address)
            wfile.write(PROTOCOL[1])
            print('UDP/Node acknowledged: ', self.client_address)
        elif rfile.readline().strip() == PROTOCOL[1]:
            self.server.antennad.add_node(self.client_address)
            print('UDP/Node registered: ', self.client_address)

class Bucket(socketserver.UDPServer):
    def __init__(self, server_address, BucketHandlerClass, antennad):
        super().__init__(server_address, BucketHandlerClass)
        self.antennad = antennad
