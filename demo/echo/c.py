#!/usr/bin/env python

import gevent
import zerorpc

c = zerorpc.Client('tcp://localhost:4242', heartbeat=1)

with c.file('/etc/passwd') as f:
    x = 0
    for line in f.readlines():
        print x, line.strip()
        x += 1
