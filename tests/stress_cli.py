#!/usr/bin/env python

import counter
from counter import zmq

context = zmq.Context()

c = zmq.Socket(context, zmq.DEALER)
c.connect('tcp://127.0.0.1:9998')

print 'running'
while True:
    c.send('', flags=zmq.SNDMORE)
    c.send('ping')
    msg = c.recv()
    counter.hit()
