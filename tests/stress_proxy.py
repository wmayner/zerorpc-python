#!/usr/bin/env python

import gevent
import gevent.queue
import counter
from counter import zmq

context = zmq.Context()


c = zmq.Socket(context, zmq.DEALER)
c.connect('tcp://127.0.0.1:9999')

s = zmq.Socket(context, zmq.ROUTER)
s.bind('tcp://127.0.0.1:9998')


class Sender(object):

    def __init__(self, socket):
        self._socket = socket
        self._send_queue = gevent.queue.Queue(maxsize=0)
        self._send_task = gevent.spawn(self._sender)

    def __del__(self):
        self.close()

    def close(self):
        if self._send_task:
            self._send_task.kill()

    def _sender(self):
        running = True
        for parts in self._send_queue:
            for i in xrange(len(parts) - 1):
                try:
                    self._socket.send(parts[i], flags=zmq.SNDMORE)
                except gevent.GreenletExit:
                    if i == 0:
                        return
                    running = False
                    self._socket.send(parts[i], flags=zmq.SNDMORE)
            self._socket.send(parts[-1])
            if not running:
                return

    def __call__(self, parts):
        self._send_queue.put(parts)


class Receiver(object):

    def __init__(self, socket):
        self._socket = socket
        self._recv_queue = gevent.queue.Queue(maxsize=0)
        self._recv_task = gevent.spawn(self._recver)

    def __del__(self):
        self.close()

    def close(self):
        if self._recv_task:
            self._recv_task.kill()

    def _recver(self):
        running = True
        while True:
            parts = []
            while True:
                try:
                    part = self._socket.recv()
                except gevent.GreenletExit:
                    running = False
                    if len(parts) == 0:
                        return
                    part = self._socket.recv()
                parts.append(part)
                if not self._socket.getsockopt(zmq.RCVMORE):
                    break
            if not running:
                break
            self._recv_queue.put(parts)

    def __call__(self):
        return self._recv_queue.get()

client_send = Sender(c)
client_recv = Receiver(c)
server_send = Sender(s)
# no server_recv since we have only one greenlet accessing it at any time.

def task(zmqid, msg):
    client_send(['', msg])
    msg = client_recv()[0]

    server_send([zmqid, msg])
    counter.hit()

print 'running'
while True:
    zmqid = s.recv()
    s.recv()
    msg = s.recv()
    gevent.spawn(task, zmqid, msg)
