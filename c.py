import zerorpc
from objref import ReqObjRef

zerorpc.Context.get_instance().register_middleware(ReqObjRef())

c = zerorpc.Client('tcp://localhost:7575')

with c.a() as a:
	print a
	print len(a)
	for x in xrange(5):
		a.append(42 + x)
		print a
	c.populateA()
	a.extend(" world")
	print a
	for i in a:
		print i
