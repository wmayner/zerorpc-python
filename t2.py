
from gevent_zerorpc import zerorpc
import gevent_zerorpc.dotcloud_middleware

import json
from pprint import pprint

class Srv(object):
    def coucou(self, a):
        '''grand doc
        
        test emncre doc
        '''
        return 'coucou ' + a

    def coucou2(self, a, b='ok'):
        '''somedoc '''
        return 'coucou ' + a + b

    def coucou3(self, a, b='ok', c='more', d=42):
        '''somedoc '''
        return 'coucou ' + a + b

    def _test(self):
        pass

    def test2(self):
        pass

s = zerorpc.Server(Srv())

r = s._zerorpc_inspect()
print json.dumps(r, indent=4)

pprint(s._methods['coucou']._functor)

s.bind('tcp://127.0.0.1:9998')
s.run()
