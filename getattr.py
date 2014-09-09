
import zerorpc

class AllMagic(object):

    def echo(self, msg):
        '''My little echo

        A big description.
        '''
        return msg

    def __getattr__(self, method):
        def functor(val=42):
            return method, val
        functor.__doc__ = '''My little {0}

        A big description about my getattred method: "{0}"
        '''.format(method)
        return functor

s = zerorpc.Server(AllMagic())
s.bind('tcp://0:9999')
s.run()
