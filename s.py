import zerorpc
from contextlib import contextmanager
from objref import objref
import logging
logging.basicConfig()

class Toto(object):

    def __init__(self, n):
        self.name = n

    def __str__(self):
        return self.name

    def fork(self, n):
        return Toto(self.name + '/' + n)

    def add(self, a, b):
        return a + b


class MyService(object):

    def __init__(self):
        self._a = []

    @objref
    @contextmanager
    def a(self):
        yield self._a

    def populateA(self):
        self._a[:] = list("hello")

    @objref
    def f(self, mode):
        return open("/tmp/f.txt", mode)

    @objref
    @contextmanager
    def toto(self, n):
        print 'Creating a new toto...', n
        try:
            yield Toto(n)
        finally:
            print 'Toto is gone :\'(', n

s = zerorpc.Server(MyService())
s.bind('tcp://127.0.0.1:7575')
s.run()
