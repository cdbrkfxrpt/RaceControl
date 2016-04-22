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
    """Handles UDP network communication.

    The NetCom class instantiates Node objects for all node IPs give in the
    config file and registers them. It then broadcasts the protocol message
    used to register with other nodes and starts threads for both the UDP
    server and the watchdog. The watchdog takes care of checking node activity
    and remove inactive nodes from the NetCom object's register.
    """
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
        """
        Adds can.Listeners to the NetCom object. These are notified by other
        objects with can.Message objects. If the listener added is not a
        can.Listener, a TypeError is raised.
        """
        if isinstance(listener, can.Listener):
            self.listeners.append(listener)
        else:
            raise TypeError('Only can.Listeners allowed.')

    def notify(self, msg):
        """
        Notifies objects from classes that implement the can.Listener interface
        with can.Message objects. Used when messages are received over the UDP
        connection.
        """
        for listener in self.listeners:
            listener(msg)

    def add_node(self, node_ip, last_msg=None):
        """
        Adds Node objects to the NetCom object.
        """
        node = Node(node_ip, last_msg)
        self.nodes.append(node)

    def ip_list(self):
        """
        Returns the IPs of all Node objects registered with the NetCom object.
        Used to return IP list externally.
        """
        ips = []
        for node in self.nodes:
            ips.append(node.ip)
        return ips

    def check_nodes(self):
        """
        Watchdog target method. Checks when a message was last received from
        all the nodes and removes Node objects from the NetCom object's
        register if they have been inactive for 5 seconds.
        """
        while self.running.is_set():
            for node in self.nodes:
                if time.perf_counter() - node.timestamp > 5:
                    self.nodes.remove(node)
                    print('Inactive node removed ', node.ip)


class Node:
    """Holds node data for all network communication partners.

    The Node class holds every communication partner's ip, the last message
    received from the partner and the time of reception.
    """
    def __init__(self, ip, last_msg=None):
        if re.match(r"(\d{1,3}\.{1}){3}\d{1,3}", ip):
            self.ip = ip
        else:
            raise TypeError('Only IPv4 addresses allowed.')

        self.last_msg = last_msg
        self.timestamp = time.perf_counter()


class Dispatcher:
    """Handles dispatching can.Message objects over the UDP connection.

    The Dispatcher object is in charge of sending CAN messages over the UDP
    connection. It offers a priority_set variable which can be used to set
    priority mode. It also holds a can.BufferedReader receiving connections
    from other RaceControl objects. It starts a thread to operate the
    connection using the operate() method.
    """
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
        """
        If priority_set is set to True, this method filters messages through
        the priority list and returns None if the message is not in the list.
        If priority_set is set to False, it returns the msg instantly.
        """
        if self.priority_set and msg.arbitration_id not in self.prioritylist:
            return None
        else:
            return msg

    def dispatch(self, payload):
        """
        Dispatches bytearrays to all nodes known to the NetCom object this
        Dispatcher object is connected to.
        """
        for node in self.netcom.nodes:
            # print('Firing payload ', payload)
            self.sock.sendto(payload, (node.ip, self.port))
        self.trigger = time.perf_counter()

    def operate(self):
        """
        Target for the thread. Reads messages from the message buffer and puts
        them into the priority filter. If they come back and are not empty, the
        operate() method puts them into the dispatch() method. Furthermore, it
        dispatches a register protocol messages to all nodes as a keepalive
        message every few seconds in case there are no CAN messages to be
        transmitted.
        """
        while self.running.is_set():
            msg = self.buffer.get_message()
            msg = self.priorityfilter(msg)
            if msg:
                self.dispatch(pickle.dumps(msg))

            if ((time.perf_counter() - self.trigger) > (self.timeout / 1000)):
                self.dispatch(PROTOCOL[0] + b'\n')


class NetComRequestHandler(socketserver.DatagramRequestHandler):
    """Inherits from socketserver.DatagramRequestHandler to handle UDP
    requests.

    For further information, read the handle() methods documentation or the
    Python library documentation for socketserver.
    """
    def handle(self):
        """
        This method reimplements the handle() method from
        socketserver.DatagramRequestHandler. It reads the incoming message.
        Through its own sender variable, it accesses the NetCom object
        associated with its UDP server object and checks if the source of the
        received message is in the node registry. If so, the timestamp for the
        node is reset and the message is filtered for protocol words, then
        passed to the NetCom object's notify() method. If not, the message is
        checked for protocol words. In case this check is successful, the
        source IP is passed to the NetCom object's add_node() method to
        register it and an appropriate response is generated and sent back to
        the source.
        """
        node_msg = self.rfile.read().strip()
        ip_list = self.server.netcom.ip_list()
        if self.client_address[0] in ip_list:
            timestamp = time.perf_counter()
            for node in self.server.netcom.nodes:
                if node.ip == self.client_address[0]:
                    node.timestamp = timestamp

            # node_msg = node_msg.split(b'#')
            # node_msg = list(msg for msg in node_msg
            #                 if msg and msg not in PROTOCOL)
            # for msg in node_msg:
            #     try:
            #         self.server.netcom.notify(pickle.loads(msg))
            #     except (pickle.UnpicklingError, EOFError):
            #         pass
            #         # syslog.write('corrupted data')
            #         # print('corrupted data received')
            #     print('Received message ', msg)

            if node_msg and node_msg not in PROTOCOL:
                try:
                    self.server.netcom.notify(pickle.loads(node_msg))
                except (pickle.UnpicklingError, EOFError):
                    pass
                    # syslog.write('corrupted data')
                    # print('corrupted data received')
                print('Received message ', node_msg)

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
    """Inherits the socketserver.UDPServer class.

    Addition made to the parent's __init__() method: Stores a reference to an
    associated NetCom object. (Should be a weak reference to not confuse the
    garbage collector but currently isn't.)
    """
    def __init__(self, server_address, NetComRequestHandlerClass, netcom):
        super().__init__(server_address, NetComRequestHandlerClass)
        self.netcom = netcom
