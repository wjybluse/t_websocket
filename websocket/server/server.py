from gevent.pywsgi import WSGIServer


class Server(WSGIServer):
    """simple websocket implement"""

    def __init__(self, application=None, handle=None, **kwargs):
        # setting handle class and other env information
        super(Server, self).__init__(self, application=application, handle_class=handle, **kwargs)
        # handle all connect from client
        self.clients = {}

    def handle(self, socket, address):
        print('handle connection from client..{}'.format(self.clients.keys()))
        handler = self.handler_class(socket, address, self)
        handler.handle()
