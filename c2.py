
import zerorpc

c = zerorpc.Client('tcp://localhost:9999', heartbeat=1)

while True:
    r = c.toto(42)
    print r
