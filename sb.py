
import zerorpc

class mylist(object):
    def __init__(self):
        self._list = [1,2,3]

    def append(self, v):
        self._list.append(v)

    def remove(self, idx):
        self._list.remove(idx)

    def dump(self):
        return self._list

class MySrv(object):

    def __init__(self, v=0):
        self._v = v
        self.mylist = mylist()

    @zerorpc.context
    def open(self, path):
        '''ca fait du caca
        
        vraiment beaucoup
        '''
        with open(path, 'w+') as f:
            yield f

    @zerorpc.context
    def hehe(self):
        yield MySrv(self._v + 1)

    def v(self):
        return self._v


    @zerorpc.context
    def pute(self):
        import os
        yield os

    @zerorpc.context
    def list(self):
        yield self.mylist

s = zerorpc.Server(MySrv(), heartbeat=1)
s.bind('tcp://127.0.0.1:9999')
s.run()
