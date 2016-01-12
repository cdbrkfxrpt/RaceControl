import socket, socketserver
import sys, threading, time
import re, pickle
import can
from cannon import Cannon
from bucket import Bucket, BucketHandler
from bridge import Bridge, BridgeHandler
from globals import S_PORT, D_PORT, PROTOCOL

class AntennaDaemon:
    def __init__(self, tcpport=S_PORT, udpport=D_PORT, listeners=[], node_ips=[]):
        # self.ip = socket.gethostbyname(socket.getfqdn())
        self.ip = '192.168.10.11'
        self.tcpport = tcpport
        self.udpport = udpport

        self.listeners = []
        for listener in listeners:
            add_listener(listener)

        self.nodes = []
        for ip in node_ips:
            add_node(ip)

        self.cannon = Cannon(self)

        bucket = Bucket(('', udpport), BucketHandler, self)
        self._bucket_server = threading.Thread(target=bucket.serve_forever)
        self._bucket_server.daemon = True
        self._bucket_server.start()

        bridge = Bridge(('localhost', tcpport), BridgeHandler, self)
        self._bridge_server = threading.Thread(target=bridge.serve_forever)
        self._bridge_server.daemon = True
        self._bridge_server.start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(PROTOCOL[0] + b'\n', ( # '255.255.255.255', self.udpport))
            re.match(r"((\d{1,3}\.{1}){3})\d{1,3}", self.ip).group(1) + '255',
            self.udpport
        ))

        self.running = threading.Event()
        self.running.set()
        self._watchdog = threading.Thread(target=self.check_nodes)
        self._watchdog.daemon = True
        self._watchdog.start()

    def add_listener(self, listener):
        if isinstance(listener, can.Listener):
            self.listeners.append(listener)
        else:
            raise TypeError('Only can.Listeners allowed.')

    def notify(self, msg):
        for listener in self.listeners:
            listener(msg)

    def add_node(self, node_ip, last_msg=None):
        node = Node(node_ip, last_msg)
        self.nodes.append(node)

    def ip_list(self):
        ips = []
        for node in self.nodes:
            ips.append(node.ip)
        return ips

    def check_nodes(self):
        while self.running.is_set():
            for node in self.nodes:
                if time.perf_counter() - node.timestamp > 5:
                    self.nodes.remove(node)
                    print('Inactive node removed ', node.ip)

class Node:
    def __init__(self, ip, last_msg=None):
        if re.match(r"(\d{1,3}\.{1}){3}\d{1,3}", ip):
            self.ip = ip
        else:
            raise TypeError('Only IPv4 addresses allowed.')

        self.last_msg = last_msg
        self.timestamp = time.perf_counter()
