
import zerorpc

SPECIAL_ATTRS = set(['__len__', '__str__', '__iter__'])

class ObjRefServer(object):

    def __init__(self, context, bufchan, obj, xheader):
          self._context = context
          self._channel = bufchan
          self._obj = obj
          self._xheader = xheader

    def serve_forever(self):
        while True:
            event = self._channel.recv()
            if event.name == "CALL":
                self._call_request(event)
            elif event.name == "GETATTR":
                self._getattr_request(event)
            elif event.name == "GETITEM":
                self._getitem_request(event)
            elif event.name == "CLOSE":
                break
            else:
                raise RuntimeError('Unknown event: {0}'.format(event.name))

    def _call_request(self, event):
        print 'call', event.args
        attr_name, args = event.args
        functor = getattr(self._obj, attr_name)
        if attr_name == '__iter__':
            streamer = zerorpc.patterns.ReqStream()
            adapted_event = zerorpc.Event(event.name, (), self._context,
                                          event.header)
            return streamer.process_call(self._context, self._channel,
                                         adapted_event, functor)
        result = functor(*args)
        self._channel.emit('OK', result, self._xheader)

    def _getattr_request(self, event):
        print 'getattr', event.args
        result = getattr(self._obj, event.args)
        self._channel.emit('OK', result, self._xheader)

    def _getitem_request(self, event):
        print 'getitem', event.args
        try:
            result = self._obj.__getitem__(event.args)
        except IndexError as e:
            self._channel.emit('IDXERR', str(e), self._xheader)
        else:
            self._channel.emit('OK', result, self._xheader)


class ObjRefClient(object):

    def __init__(self, context, bufchan, req_event, rep_event,
            handle_remote_error, xheader):
        self._context = context
        self._channel = bufchan
        self._req_event = req_event
        self._rep_event = rep_event
        self._handle_remote_error = handle_remote_error
        self._xheader = xheader

    def _select_pattern(self, event):
        for pattern in self._context.hook_client_patterns_list(
                patterns.patterns_list):
            if pattern.accept_answer(event):
                return pattern
        msg = 'Unable to find a pattern for: {0}'.format(event)
        raise RuntimeError(msg)

    def _request(self, event_name, args):
        self._channel.emit(event_name, args, self._xheader)
        event = self._channel.recv()
        if event.name == 'IDXERR':
            raise IndexError(event.args)
        pattern = self._select_pattern(event)
        return pattern.process_answer(self._context, self._channel,
                                      self._req_event, event)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self._channel.close()
        else:
            self._channel.emit('CLOSE', None, self._xheader)
            self._context.hook_client_after_request(self._req_event, event)
            self._channel.close()

    def __getitem__(self, key):
        return self._request('GETITEM', key)

    def __call__(self, name, *args):
        return self._request('CALL', (name, args))

    def __getattr__(self, method):
        return lambda *args, **kargs: self(method, *args, **kargs)


class ReqObjRef:

    def process_call(self, context, bufchan, req_event, functor):
        context.hook_server_before_exec(req_event)
        xheader = context.hook_get_task_context()

        with functor(*req_event.args) as obj:
            objserver = ObjRefServer(context, bufchan, obj, xheader)

            open_event = bufchan.new_event(
                    'OBJREF', [a for a in SPECIAL_ATTRS if hasattr(obj, a)],
                    xheader)
            context.hook_server_after_exec(req_event, open_event)
            bufchan.emit_event(open_event)

            objserver.serve_forever()

    def accept_answer(self, event):
        return event.name == 'OBJREF'

    def process_answer(self, context, bufchan, req_event, rep_event,
            handle_remote_error):

        class ObjRefClientWithSpecials(ObjRefClient):
            pass

        for attr in SPECIAL_ATTRS.intersection(rep_event.args):
            def wf(attr):
                def f(self, *args):
                    return self(attr, *args)
                f.__name__ = attr
                return f
            setattr(ObjRefClientWithSpecials, attr, wf(attr))

        objclient = ObjRefClientWithSpecials(context, bufchan, req_event,
                                             rep_event, handle_remote_error,
                                             context.hook_get_task_context())
        return objclient

    def client_patterns_list(self, patterns):
        patterns.append(self)
        return patterns


class objref(zerorpc.decorators.DecoratorBase):
    pattern = ReqObjRef()
