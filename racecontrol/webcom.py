#!/usr/bin/python3
# -*- coding:utf-8 -*-

import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue

from flask import Flask
from flask import Response
from flask import render_template

import can
import time
import threading


class GUIGenerator:
    def __init__(self, queue, msgfilter):
        self.queue = queue
        self.msgfilter = msgfilter
        self.buffer = can.BufferedReader()

        self._running = threading.Event()
        self._running.set()

        self._generator = threading.Thread(target=self.generate)
        self._generator.daemon = True

        self._generator.start()

    def generate(self):
        while self._running.is_set():
            msg = self.buffer.get_message()
            if msg and msg.arbitration_id == self.msgfilter[0]:
                data = ''
                for i in range(1, 6, 2):
                    for j in range(self.msgfilter[i+1]):
                        data += str(msg.data[self.msgfilter[i] + j])
                    data += ','

                # print(data[:-1])
                self.queue.put(data[:1])


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
        print("%s\n\n" % "\n".join(lines))
        return "%s\n\n" % "\n".join(lines)


app = Flask('racecontrol')

subscriptions = []

upperqueue = Queue()
lowerqueue = Queue()
textqueue = Queue()


@app.route('/')
def data():
    return render_template('data.html')


@app.route('/loggings')
def loggings():
    return render_template('loggings.html')


@app.route('/upper')
def upper():
    def gen():
        subscriptions.push(0)
        try:
            while True:
                data = upperqueue.get()
                ev = DataStream(data)
                yield ev.encode()
        except GeneratorExit:
            subscriptions.remove(0)

    return Response(gen(), mimetype="text/event-stream")


# @app.route('/publish')
# def publish():
#     def notify():
#         msg = str(time.time())
#         for sub in subscriptions[:]:
#             sub.put(msg)

#     gevent.spawn(notify)
#     return "OK"


@app.route('/debug')
def debug():
    return "Currently %s subscriptions." % len(subscriptions)


if __name__ == '__main__':
    app.debug = True
    server = WSGIServer(("", 5000), app)
    server.serve_forever()
