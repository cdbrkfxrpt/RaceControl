import socket, socketserver
import pickle

class BucketHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        if self.client_address in self.server.antennad.nodes:
            msglist = rfile.read().split(b'#')
            msglist = list(filter(None, msglist))
            for msg in msglist:
                try:
                    print('Received message ', msg)
                    self.server.antennad.notify(pickle.loads(msg))
                except pickle.UnpicklingError:
                    # self.errlog.write('corrupted data')
                    print('corrupted data received')

class Bucket(socketserver.UDPServer):
    def __init__(self, server_address, BucketHandlerClass, antennad):
        super().__init__(server_address, BucketHandlerClass)
        self.antennad = antennad
