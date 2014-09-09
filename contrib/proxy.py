#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Open Source Initiative OSI - The MIT License (MIT):Licensing
#
# The MIT License (MIT)
# Copyright (c) 2014  François-Xavier Bourlet (bombela@gmail.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import gevent
import zerorpc
import zmq
import logging

logger = logging.getLogger(__name__)

# ZMQ_PROBE_ROUTER

class Proxy(object):

    def __init__(self, context=None):
        self._context = context or zerorpc.Context.get_instance()
        self._frontend = zmq.Socket(self._context, zmq.ROUTER)
        if zmq.zmq_version_info() >= (4, 0, 0):
            self._backend = zmq.Socket(self._context, zmq.ROUTER)
            self._frontend.setsockopt(zmq.PROBE_ROUTER, 1)
            self._backend.setsockopt(zmq.PROBE_ROUTER, 1)
        else:
            self._backend = zmq.Socket(self._context, zmq.DEALER)

    def _resolve_endpoint(self, endpoint, resolve):
        if resolve:
            endpoint = self._context.hook_resolve_endpoint(endpoint)
        if isinstance(endpoint, (tuple, list)):
            r = []
            for sub_endpoint in endpoint:
                r.extend(self._resolve_endpoint(sub_endpoint, resolve))
            return r
        return [endpoint]

    def _connect(self, name, socket, endpoint, resolve):
        r = []
        for endpoint_ in self._resolve_endpoint(endpoint, resolve):
            logger.info('Connecting %s to %s', name, endpoint_)
            r.append(socket.connect(endpoint_))
        return r

    def _bind(self, name, socket, endpoint, resolve):
        r = []
        for endpoint_ in self._resolve_endpoint(endpoint, resolve):
            logger.info('Binding %s to %s', name, endpoint_)
            r.append(socket.bind(endpoint_))
        return r

    def connect_frontend(self, endpoint, resolve=True):
        return self._connect('frontend', self._frontend, endpoint, resolve)

    def bind_frontend(self, endpoint, resolve=True):
        return self._bind('frontend', self._frontend, endpoint, resolve)

    def connect_backend(self, endpoint, resolve=True):
        return self._connect('backend', self._backend, endpoint, resolve)

    def bind_backend(self, endpoint, resolve=True):
        return self._bind('backend', self._backend, endpoint, resolve)

    def run_forever(self):
        logger.info('Starting zerorpc proxy...')
        zmq.proxy(self._frontend, self._backend)


if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description='''Start a zerorpc proxy.
        Note the proxy is fully symmetric and there is no technical differences
        between frontend and backend.
        '''
    )
    parser.add_argument('--connect_frontend', action='append',
            metavar='frontend_address', help='''specify address to connect to.
            Can be specified multiple times and in conjunction with --bind''')
    parser.add_argument('--bind_frontend', action='append', metavar='address',
            help='''specify address to listen to. Can be specified multiple
            times and in conjunction with --connect''')
    parser.add_argument('--connect_backend', action='append',
            metavar='backend_address', help='''specify address to connect to.
            Can be specified multiple times and in conjunction with --bind''')
    parser.add_argument('--bind_backend', action='append', metavar='address',
            help='''specify address to listen to. Can be specified multiple
            times and in conjunction with --connect''')
    parser.add_argument('frontend_endpoint', nargs='?', help='''endpoint to bind
    the frontend to. Skip this if you specified any --frontend/backend_connect or
    --frontend/backend_bind at least once''')
    parser.add_argument('backend_endpoint', nargs='?', help='''endpoint to bind
    the backend to. Skip this if you specified any --frontend/backend_connect or
    --frontend/backend_bind at least once''')
    
    args = parser.parse_args()

    if not (args.bind_frontend or args.connect_frontend or args.frontend_endpoint):
        print 'Missing frontend endpoint'
        parser.print_help()
    if not (args.bind_backend or args.connect_backend or args.backend_endpoint):
        print 'Missing backend endpoint'
        parser.print_help()
    
    proxy = Proxy()
    
    def setup_links(name):
        bind = getattr(proxy, 'bind_' + name)
        connect = getattr(proxy, 'connect_' + name)
        endpoints = getattr(args, 'bind_' + name) or []
        endpoints.append(getattr(args, name + '_endpoint'))
        for endpoint in filter(None, endpoints):
            bind(endpoint)
        for endpoint in getattr(args, 'connect_' + name) or []:
            connect(endpoint)

    setup_links('frontend')
    setup_links('backend')
    proxy.run_forever()
