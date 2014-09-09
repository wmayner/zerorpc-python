# zmq.green exists, why not using it?

Since zmq.green is now officially part of pyzmq, why not using it rather than
zerorpc.gevent\_zmq.

On a simple benchmark:
 - an echo server (receive a message, send it back)
 - a proxy server (receive a message, spawn a proxy task which forward the
   message to the server, then wait and forward the response to the client)
 - a client that send a message to the proxy and wait for the answer in an
   infinite loop

Running with on server, one proxy, and one client:

 metric               | server CPU | proxy CPU | client CPU | #req/s 
--------------------------------------------------------------------
 zmq.green            |        30% |       80% |        26% |  2300
 zerorpc.gevent\_zmq  |        26% |       82% |        25% |  3000
--------------------------------------------------------------------

Same with two clients:

 metric               | server CPU | proxy CPU | clients CPU / #req/s 
-----------------------------------------------------------------------
 zmq.green            |        42% |      112% | 21% / 1800, 20% / 1800
 zerorpc.gevent\_zmq  |         2% |       10% |  1% /  100,  1% /  100
-----------------------------------------------------------------------

There is an strange bug between gevent and zmq, sometimes, gevent will miss an
event from zmq. It is not clear if the problem comes from gevent or zmq. Both
zmq.green and zerorpc.gevent\_zmq work around it by polling zmq when no events
are received for a little while.

In practice, it seems that with more than one client, zerorpc.gevent\_zmq
misses a shitload of events on the proxy, definitively killing the
performances. zmq.green however, doesn't miss any event at all, and scale way
better! Running more clients shows the same thing.
