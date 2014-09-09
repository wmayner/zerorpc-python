
import zerorpc

class MySrv(object):
    def toto(self, a):
        print 'toto', a
        return a * 2

s = zerorpc.Server(MySrv(), heartbeat=1)
s.bind('tcp://127.0.0.1:9999')
s.run()
