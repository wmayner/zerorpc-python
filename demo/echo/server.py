#!/usr/bin/env python

import gevent
import zerorpc

class Echo(object):

    def __init__(self, prefix='echo'):
        self._prefix = prefix

    def echo(self, msg):
        '''My little echo

        Some doc here.
        '''
        msg = '{0} {1}'.format(self._prefix, msg)
        print msg
        return msg

    def __repr__(self):
        return 'Echo({0})'.format(self._prefix)

    @zerorpc.context
    def file(self, path):
        try:
            with open(path, 'r') as f:
                yield f
            print f, 'closed cleanly!'
        except Exception as e:
            print f, 'closed on error!', e
            raise

    @zerorpc.context
    def rebound(self, prefix):
        try:
            yield Echo('{0} {1}'.format(self._prefix, prefix))
        except Exception as e:
            print 'rebound ERR', e
            raise
        else:
            print 'rebound DONE'

    def sleep(self, seconds):
        seconds = int(seconds)
        print 'sleeping {0}s'.format(seconds)
        gevent.sleep(seconds)

    @zerorpc.stream
    def xrange(self, a, b):
        try:
            for x in xrange(int(a), int(b)):
                print x
                yield x
                gevent.sleep(0)
        except Exception:
            print 'il s est casse comme un connard'
        finally:
            print 'c est fini'

s = zerorpc.Server(Echo())
s.bind('tcp://0:4242')
print 'running...'
s.run()
