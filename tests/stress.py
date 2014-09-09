#!/usr/bin/env python

import counter
from counter import zmq

context = zmq.Context()

s = zmq.Socket(context, zmq.ROUTER)
s.bind('tcp://127.0.0.1:9999')
print 'running'

while True:
    zmqid = s.recv()
    s.recv()
    msg = s.recv()
    s.send(zmqid, flags=zmq.SNDMORE)
    s.send(msg)
    counter.hit()
