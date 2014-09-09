
import time
import gevent

ts_serie = None
cnt_serie = [0]

def print_counter():
    global ts_serie, cnt_serie
    global cnt_serie_last, ts_serie_last
    while True:
        gevent.sleep(1)
        now = time.time()
        start = ts_serie[0]
        cnt_sum = sum(cnt_serie)
        print float(cnt_sum) / float(now - start), 'rq/s'
        ts_serie.append(now)
        cnt_serie.append(0)
        if len(cnt_serie) > 3:
            cnt_serie.pop(0)
            ts_serie.pop(0)

def hit():
    global ts_serie
    global cnt_serie
    if ts_serie is None:
        ts_serie = [time.time()]
        gevent.spawn(print_counter)
    cnt_serie[-1] += 1

import os
if os.path.exists('green'):
    import zmq.green as zmq
else:
    import zerorpc.gevent_zmq as zmq
