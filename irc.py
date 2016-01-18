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
        self.server = None
        self.nicks = nicks
        self.pwd = pwd
        self.encoding = encoding
        self.__lines = [b'']
        self.__nickidx = 0

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
                            self.initial_auth,
                            server_hostname=self.host)

    def initial_auth(self):
        self.__auth()
        self.stream.read_until_close(self.closed, self.route)

    def send(self, data: str):
        """
        Write to stream
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
        # Inspircd resends lines that came through incomplete
        # other ircd's have not been tested.
        data = data.split(b'\r\n')
        self.__lines = data

    def route(self, data):
        """
        Monitor incoming data and dispatch it to the proper methods
        :param data: Raw byte array
        """
        self.recv(data)
        for line in self.__lines:
            if line != b'':
                response = line.split(b':')
                if b'' in response: response.remove(b'')

                # Get the response message
                message = response[1:]
                message = b''.join(message)

                # Get the response code
                code = response[0].split(b' ')
                if len(code) <= 2:
                    code = response[0].strip()
                else:
                    code = code[1].strip()

                if code == b'ERROR':
                    pass
                # Respond to ping
                elif code == b'PING':
                    ping = line.split(b' ')
                    server1 = ping[1]
                    server2 = ping[2] if len(ping) == 3 else None
                    self.pong(server1, server2)
                else:
                    if code == b'433':
                        self.__nick_in_use()

                # print('Code: %s, %s' % (code, line.decode(self.encoding)))
                print('Code: %s, %s' % (code, message.decode(self.encoding)))

    def __auth(self):
        if self.__nickidx < len(self.nicks):
            nick = self.nicks[self.__nickidx]
        else:
            nick = self.nicks[0] + str(self.__nickidx - len(self.nicks))
        self.send('NICK %s' % nick)
        self.send('USER %s 0 * :%s' % (self.nicks[0], 'realname'))

    def __nick_in_use(self):
        """

        :return:
        """
        self.__nickidx += 1
        self.__auth()

    def pong(self, server1, server2):
        """
        Send PONG response
        :param server1:
        :param server2:
        """
        if server2:
            self.send(b'PONG %s %s' % (server1, server2))
        else:
            self.send(b'PONG %s' % server1)

    def closed(self, data):
        pass
