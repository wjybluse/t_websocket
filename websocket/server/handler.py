from gevent.pywsgi import WSGIHandler
from . import *
import base64
import hashlib
from .stream import Stream, Payload


class WebSocketHandler(WSGIHandler):
    """ handle the real message"""

    def __init__(self, socket, address, server):
        # do init the websocket handler
        super(WebSocketHandler, self).__init__(socket, address, server)

    def upgrade_websocket(self):
        print('handle websocket request from client,begin validate')
        method = self.environ['METHOD']
        # first http request is get
        if method.upper() is not 'GET':
            print('cannot update to websocket only get method')
            return
        if self.request_version != 'HTTP/1.1':
            self.start_response('402 Bad Request', [])
            print('Invalid http version')
            return ['Invalid http version']
        version = self.environ.get('HTTP_SEC_WEBSOCKET_VERSION')
        if version is None or version not in VERSION:
            print(
                'current websocket does not supported.current_version={},supported_version={}', version,
                ','.join(VERSION))
            # resp header format Sec-WebSocket-Version:xx,xx1,xx2
            self.start_response('400 Bad Request', [('Sec-WebSocket-Version', ','.join(VERSION))])
            return ['current websocket does not supported.current_version={},supported_version={}', version,
                    ','.join(VERSION)]
        sec_key = self.environ.get('Sec-WebSocket-Key'.upper(), '')

        if sec_key is None:
            self.start_response('400 Bad Request', [])
            return ['Sec-WebSocket-Key is empty']

        key_len = 0
        try:
            key_len = len(base64.b64decode(sec_key))
        except Exception, e:
            print('decode sec websocket key failed {}'.format(e))
            self.start_response('400 Bad Request', [])
            return ['Key is not base64 encode']
        if key_len != 16:
            print('Invalid sec key error.sec key ')
            self.start_response('400 Bad Request', [])
            return ['Invalid sec websocket key len']
        protocol = self.environ.get('HTTP_SEC_WEBSOCKET_PROTOCOL')
        if protocol is None:
            self.start_response('400 Bad Request', [])
            return ['Invalid protocol']
        # after validate the header params
        self._wesocket = WebSocket(self, Stream(self))
        self.environ.update({'wsgi.websocket.version': version, 'wsgi.websocket': self._wesocket})
        upgrade_headers = [('Upgrade', 'websocket'), ('Connection', 'Upgrade'),
                           ('Sec-WebSocket-Accept', base64.b64encode(hashlib.sha1(sec_key + APPEND_ID)).digest())]
        if protocol:
            upgrade_headers.append(('Sec-WebSocket-Protocol', protocol))
        self.start_response('101 Switching Protocols', upgrade_headers)

    def start_response(self, status, headers, exc_info=None):
        writer = super(WebSocketHandler, self).start_response(status, headers, exc_info)
        self._handle_websocket()
        return writer

    def _handle_websocket(self):
        if not self.environ.get('wsgi.websocket'):
            return
        # disable all connection
        self.provided_content_length = False
        self.response_use_chunked = False
        self.close_connection = True
        self.provided_date = True

    def run_application(self):
        self.result = self.upgrade_websocket()
        if hasattr(self, 'websocket'):
            if self.status and not self.headers_sent:
                self.write('')
            self._run_websocket()
            return super(WebSocketHandler, self).run_application()
        if self.status:
            if not self.result:
                self.result = []
            self._handle_result()
        return super(WebSocketHandler, self).run_application()

    def _run_websocket(self):
        self.server.clients[self.client_address] = Client(self.client_address, self._wesocket)
        try:
            self.application(self.environ, lambda s, h: [])
        finally:
            del self.server.clients[self.client_address]
            if not self._wesocket.closed:
                self._wesocket.close()

    def _handle_result(self):
        pass


class WebSocket(object):
    def __init__(self, env, stream, handler):
        self.env = env
        self.stream = stream
        self.handler = handler

    def handle(self):
        pass

    def close(self):
        self.stream.close()

    @property
    def closed(self):
        return True


class Client(object):
    def __init__(self, client, ws):
        """
        :param client: connection of client
        :param ws: websocket
        :return:
        """
        super(Client, self).__init__()
        self.client = client
        self.ws = ws
