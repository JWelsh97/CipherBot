import tornado
import tornado.iostream
import socket
import ssl


class IRC(object):
    def __init__(self, host: str, port: int, nicks: list, pwd: str,
                 use_ssl: bool=False, ssl_options: ssl.SSLContext=None,
                 encoding: str='utf-8'):
        self.host = host
        self.port = port
        self.nicks = nicks
        self.pwd = pwd
        self.encoding = encoding
        self.__lines = [b'']

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

        if use_ssl:
            if not ssl_options:
                ssl_options = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                ssl_options.verify_mode = ssl.CERT_NONE
            sock = ssl.wrap_socket(sock, do_handshake_on_connect=False)
            self.stream = tornado.iostream.SSLIOStream(sock, ssl_options=ssl_options)
        else:
            self.stream = tornado.iostream.IOStream(sock)

        self.stream.connect((self.host, self.port),
                            self.auth,
                            server_hostname=self.host)

    def auth(self):
        self.send('NICK %s' % self.nicks[0])
        self.send('USER %s 0 * :%s' % (self.nicks[0], 'realname'))
        self.stream.read_until_close(self.closed, self.route)

    def send(self, data: str):
        """
        Write data to stream
        :param data: String to send
        :return:
        """
        if type(data) is str:
            data = data.encode(self.encoding)

        if type(data) is bytes:
            self.stream.write(data + b'\r\n')
        else:
            raise TypeError('Data must be a byte or string')

    def recv(self, data):
        """
        Split received data into lines
        :param data: Bytes received
        :return:
        """
        data = data.split(b'\r\n')
        self.__lines = data

    def route(self, data):
        self.recv(data)
        for line in self.__lines:
            if line != b'':
                # Respond to ping
                if line.startswith(b'PING :'):
                    ping = line.split(b' ')
                    server1 = ping[1]
                    server2 = ping[2] if len(ping) == 3 else None
                    self.pong(server1, server2)
                print(line.decode(self.encoding))

    def pong(self, server1, server2):
        if server2:
            self.send(b'PONG %s %s' % (server1, server2))
        else:
            self.send(b'PONG %s' % server1)

    def closed(self, data):
        pass
