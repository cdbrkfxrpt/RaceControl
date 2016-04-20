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


from flask import Flask
from flask import Response
from flask import render_template

import struct
import can
import threading
import multiprocessing


class GUICom:
    def __init__(self, queue, msgfilter):
        self.queue = queue
        self.msgfilter = msgfilter

        self.buffer = can.BufferedReader()

        self.permsg = []
        for i in range(9):
            self.permsg.append(0)

        self._running = threading.Event()
        self._running.set()

        self._generator = threading.Thread(target=self._generate)
        self._generator.daemon = True

        self._generator.start()

    def _generate(self):
        unpackdict = {2: 'H', 4: 'f', 8: 'd'}
        while self._running.is_set():

            msg = self.buffer.get_message(0.5)
            if msg and msg.arbitration_id in self.msgfilter:

                for k, v in self.msgfilter[msg.arbitration_id].items():
                    start = v['start']
                    size = v['size']
                    end = start + size
                    if v['size'] > 1:
                        self.permsg[k] = (struct.unpack(unpackdict[size],
                                          msg.data[start:end])[0])
                    else:
                        self.permsg[k] = msg.data[start]

                self.queue.put(','.join(str(el) for el in self.permsg))


class DataStream:
    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data: "data",
            self.event: "event",
            self.id: "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k)
                 for k, v in self.desc_map.items() if k]
        return "%s\n\n" % "\n".join(lines)


app = Flask('racecontrol')

subscriptions = []
msgqueue = multiprocessing.Queue()


@app.route('/')
def data():
    return render_template('data.html')


@app.route('/loggings')
def loggings():
    return render_template('loggings.html')


@app.route('/subscribe')
def subscribe():
    def gen():
        subscriptions.append(0)
        try:
            while True:
                data = msgqueue.get(True)
                if data:
                    print(data)
                    ev = DataStream(data)
                    yield ev.encode()
        except GeneratorExit:
            subscriptions.remove(0)

    return Response(gen(), mimetype="text/event-stream")


@app.route('/debug')
def debug():
    return "Currently %s subscriptions." % len(subscriptions)
