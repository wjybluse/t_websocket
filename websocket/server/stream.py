class Stream(object):
    # define special property use slots
    __slots__ = ('handler', 'reader', 'writer')

    def __init__(self, handler):
        self.reader = handler.rfile.read
        self.writer = handler.socket.sendall
        self.handler = handler


class Payload(object):
    __slots__ = ('fin', 'opcode', 'flags', 'length', 'mask')

    def __init__(self, fin=0, opcode=0, flags=0, length=0):
        """
        :param fin: fin code
        :param opcode: opcode
        :param flags: flags
        :param length: payload length
        :return:
        """
        self.fin = fin
        self.opcode = opcode
        self.flags = flags
        self.length = length

    @staticmethod
    def decode_header(data):
        pass

    @staticmethod
    def encode_header(data):
        pass

    def mask_payload(self, payload):
        byte_payload = bytearray(payload)
        byte_mask = bytearray(self.mask)
        # maske payload and create str
        # the max length bit of mask is 4
        for i in xrange(self.length):
            byte_payload[i] ^= byte_mask[i % 4]
        return str(byte_payload)

    def __repr__(self):
        return (
            'header fin={0},opcode={1},mask={2},flags={3},length={4},klass={5}'.format(self.fin, self.opcode, self.mask,
                                                                                       self.flags,
                                                                                       self.length, id(self)))
