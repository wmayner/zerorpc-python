from unittest import TestCase
from time import time
from gevent import spawn, sleep, event
from gevent.subprocess import Popen
from zerorpc import Server, Client


class Service(object):
    def hello(self):


class BackgroundJobTestCase(TestCase):
    def setUp(self):
        self.stop_event = event.Event()
        self.background_job = spawn(self._start_job)

    def _start_job(self):
        while not self.stop_event.is_set():
            Popen("sleep 1", shell=True).wait()  # this does not work
            # sleep(1)  # this works

    def tearDown(self):
        self.stop_event.set()
        self.background_job = self.background_job.join()

    def test_rpc_with_background_job_for_longer_periods(self, duration_in_seconds=600):
        server = Server(Service())
        server.bind("tcp://127.0.0.1:7001")
        spawn(server.run)
        client = Client()
        client.connect("tcp://127.0.0.1:7001")
        start_time = time()
        while abs(time() - start_time) <= duration_in_seconds:
            client.get_nothing()

