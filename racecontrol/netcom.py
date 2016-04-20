# RaceControl, a bidirectional CAN bus telemetry platform.
# Copyright (C) 2016 Florian Eich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import socketserver
import threading
import time
import pickle
import re
import can

from racecontrol.globals import D_PORT, PROTOCOL, NODES


class NetCom:
    def __init__(self, prioritylist, ip='192.168.11.26', udpport=D_PORT,
                 listeners=[], node_ips=NODES):
        self.ip = ip
        self.udpport = udpport

        self.listeners = []
        for listener in listeners:
            self.add_listener(listener)

        self.nodes = []
        for node_ip in node_ips:
            self.add_node(node_ip)
            print('Starting up with node ', node_ip)

        self.dispatcher = Dispatcher(self, prioritylist)

        netcomserver = NetComServer(('', self.udpport),
                                    NetComRequestHandler, self)
        self._netcom_server = threading.Thread(
                target=netcomserver.serve_forever
        )
        self._netcom_server.daemon = True
        self._netcom_server.start()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(PROTOCOL[0] + b'\n', (
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


class Dispatcher:
    def __init__(self, netcom, prioritylist, port=D_PORT, timeout=100):
        self.buffer = can.BufferedReader()

        self.prioritylist = prioritylist
        self.priority_set = False

        self.netcom = netcom
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.timeout = timeout
        self.trigger = time.perf_counter()

        self.running = threading.Event()
        self.running.set()

        self._mechanism = threading.Thread(target=self.operate)
        self._mechanism.daemon = True

        self._mechanism.start()

    def priorityfilter(self, msg):
        if self.priority_set and msg.arbitration_id not in self.prioritylist:
            return None
        else:
            return msg

    def dispatch(self, payload):
        for node in self.netcom.nodes:
            # print('Firing payload ', payload)
            self.sock.sendto(payload, (node.ip, self.port))
        self.trigger = time.perf_counter()

    def operate(self):
        while self.running.is_set():
            msg = self.buffer.get_message()
            msg = self.priorityfilter(msg)
            if msg:
                self.dispatch(pickle.dumps(msg))

            if ((time.perf_counter() - self.trigger) > (self.timeout / 1000)):
                self.dispatch(PROTOCOL[0] + b'\n')


class NetComRequestHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        node_msg = self.rfile.read().strip()
        ip_list = self.server.netcom.ip_list()
        if self.client_address[0] in ip_list:
            timestamp = time.perf_counter()
            for node in self.server.netcom.nodes:
                if node.ip == self.client_address[0]:
                    node.timestamp = timestamp

            node_msg = node_msg.split(b'#')
            node_msg = list(msg for msg in node_msg
                            if msg and msg not in PROTOCOL)
            for msg in node_msg:
                try:
                    self.server.netcom.notify(pickle.loads(msg))
                except (pickle.UnpicklingError, EOFError):
                    pass
                    # syslog.write('corrupted data')
                    # print('corrupted data received')
                print('Received message ', msg)

        elif (node_msg == PROTOCOL[0] and not
              self.client_address[0] == self.server.netcom.ip and not
              self.client_address[0] == '127.0.0.1'):
            self.server.netcom.add_node(self.client_address[0], node_msg)
            print('UDP/Node acknowledged: ', self.client_address[0])
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(PROTOCOL[1], (self.client_address[0], D_PORT))
        elif (node_msg == PROTOCOL[1] and not
              self.client_address[0] == self.server.netcom.ip_list and not
              self.client_address[0] == '127.0.0.1'):
            self.server.netcom.add_node(self.client_address[0], node_msg)
            print('UDP/Node registered: ', self.client_address[0])


class NetComServer(socketserver.UDPServer):
    def __init__(self, server_address, BucketHandlerClass, netcom):
        super().__init__(server_address, BucketHandlerClass)
        self.netcom = netcom
