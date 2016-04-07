import inspect
import socket
import ssl
import re
import tornado
import tornado.iostream
from tornado.ioloop import IOLoop


class IRC(object):
    def __init__(self, host: str, port: int, nicks: list, pwd: str, chans: list, op_pass: str,
                 use_ssl: bool=False, ssl_options: ssl.SSLContext=None,
                 encoding: str='utf-8'):
        """
        Asynchronous IRC client
        :param host: Server address
        :param port: IRC Port
        :param nicks: List of nicknames to try
        :param pwd: NickServ password
        :param use_ssl: Enable/Disable SSL
        :param ssl_options: SSLContext object
        :param encoding: Character encoding to use
        """
        self.host = host
        self.port = port
        self.nicks = nicks
        self.pwd = pwd
        self.chans = chans
        self.oper_pass = op_pass
        self.ssl = use_ssl
        self.encoding = encoding
        self.__nickidx = 0
        self.__handlers = {
            b'PING': self.__ping,
            b'NOTICE': self.__notice,
            b'PRIVMSG': self.__privmsg,
            b'PART': self.__part,
            b'JOIN': self.__join,
            b'MODE': self.__mode,
            b'NICK': self.__nick,
            b'QUIT': self.__quit,
            b'KICK': self.__kick,
            b'001': self.__welcome,
            b'251': self.__user_count,
            b'252': self.__op_count,
            b'353': self.__namreply,
            b'372': self.__motd,
            b'376': self.__end_motd,
            b'433': self.__nick_in_use,
            b'900': self.__logged_in
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

        if use_ssl:
            if not ssl_options:
                ssl_options = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                # IRC often has unsigned certs, by default do not verify
                ssl_options.verify_mode = ssl.CERT_NONE
            sock = ssl.wrap_socket(sock, do_handshake_on_connect=False)
            self.stream = tornado.iostream.SSLIOStream(sock, ssl_options=ssl_options)
        else:
            self.stream = tornado.iostream.IOStream(sock)

        self.stream.connect((self.host, self.port),
                            self.__initial_auth,
                            server_hostname=self.host)

    def __initial_auth(self):
        """
        Start listening for data
        """
        self.send('USER %s 0 * :%s' % (self.nicks[0], 'realname'))
        self.__set_nick()
        self.stream.read_until_close(self.closed, self.__route)

    def __route(self, data):
        """
        Dispatch incoming data to the proper methods
        :param data: Raw byte array
        """
        data = data.split(b'\r\n')
        prefix = b''
        idx = 0

        for line in data:
            if line:
                if line.startswith(b':'):
                    idx = line.find(b' ')
                    prefix = line[1:idx]
                else:
                    idx = 0

                irc_msg = line[idx+1 if idx > 0 else idx:].split(b' :')
                message = b''.join(irc_msg[1:]).strip()
                irc_msg = irc_msg[0].split(b' ')
                command = irc_msg[0]
                params = irc_msg[1:]

                if command in self.__handlers.keys():
                    handler = self.__handlers[command]
                    kwargs = inspect.signature(handler).parameters.keys()
                    if len(inspect.signature(handler).parameters) > 0:
                        irc_args = {'prefix': prefix,
                                    'command': command,
                                    'params': params,
                                    'message': message}
                        kwargs = {k: irc_args[k] for k in irc_args if k in kwargs}
                        handler(**kwargs)
                    else:
                        handler()
                else:
                    print(line)
                    print('(Unhandled) Pfx: %s,Cmd: %s,Param: %s, Msg: %s' % (prefix, command, params, message))

    def __send_auth(self):
        """
        Send auth data
        """
        self.__set_nick()
        if self.pwd:
            self.send('PRIVMSG nickserv IDENTIFY %s' % self.pwd)
        if self.oper_pass:
            self.send('OPER %s %s' % (self.nicks[0], self.oper_pass))
            self.send('PRIVMSG operserv login %s' % self.oper_pass)

    def __set_nick(self):
        """
        Set a nick
        """
        if self.__nickidx < len(self.nicks):
            nick = self.nicks[self.__nickidx]
        else:
            nick = self.nicks[0] + str(self.__nickidx - len(self.nicks))
        self.send('NICK %s' % nick)

    @staticmethod
    def __get_nick(prefix):
        """
        Parse prefix data
        :param prefix: nick!user@host
        :return: Nickname as byte array
        """
        return prefix.split(b'!')[0]

    def __nick_in_use(self):
        """
        Try another nick
        """
        self.__nickidx += 1
        self.__send_auth()

    def __ping(self, message):
        """
        Ping event handler
        :param message: PING message
        """
        ping = message.split(b' ')
        server1 = ping[0].decode(self.encoding)
        server2 = ping[1].decode(self.encoding) if len(ping) == 2 else ''

        if server2:
            self.send('PONG %s %s' % (server1, server2))
        else:
            self.send('PONG %s' % server1)
        self.ping(server1, server2)

    def __motd(self, message):
        """
        MOTD handler
        :param message: MOTD line
        """
        self.motd(message.decode(self.encoding))

    def __notice(self, prefix, params, message):
        """
        Notice handler
        :param params: Parameter list
        :param message: Notice message
        """
        nick = self.__get_nick(prefix)
        self.notice(nick.decode(self.encoding),
                    [p.decode(self.encoding) for p in params],
                    message.decode(self.encoding))

    def __privmsg(self, prefix, params, message):
        """
        PRIVMSG event handler
        :param prefix: Sender
        :param params: Command parameters
        :param message: PRIVMSG message
        """
        self.privmsg(prefix.decode(self.encoding),
                     params[0].decode(self.encoding),
                     message.decode(self.encoding, 'ignore'))

    def __part(self, prefix, params, message):
        """
        PART event handler
        :param prefix: Sender
        :param params: User, Channel
        :param message: Part message
        """
        self.user_parted(self.__get_nick(prefix).decode(self.encoding),
                         params[0].decode(self.encoding),
                         message.decode(self.encoding))

    def __join(self, prefix, message):
        """
        JOIN event handler
        :param prefix: User
        :param message: Channel
        """
        # Sometimes the channel ends up in params because the server
        # doesn't send a : after the JOIN command. This appears to only
        # happen when a user is changing vhosts so there is no reason to
        # resend the JOIN message down stream.
        if message:
            self.user_joined(self.__get_nick(prefix).decode(self.encoding),
                             message.decode(self.encoding))

    def __mode(self, prefix, params, message):
        """
        MODE event handler
        :param prefix: User
        :param params: channel, target, modes
        """
        source = self.__get_nick(prefix).decode(self.encoding)
        if params[0].startswith(b'#'):
            channel = params[0].decode(self.encoding)
            mode = params[1].decode(self.encoding)
            target = params[2].decode(self.encoding) if len(params) > 2 else params[0].decode(self.encoding)
            self.channel_mode(source, channel, mode, target)
        else:
            target = params[0].decode(self.encoding)
            if len(params) > 1:
                mode = [x for x in params[1].decode(self.encoding)]
            else:
                mode = [x for x in message.decode(self.encoding)]

            self.user_mode(source, target, mode)

    def __user_count(self, message):
        """
        Command 251 event handler
        :param message: User, Service, Servers
        """
        reg = re.compile(r'[\w\s]+?(\d+)[\w\s]+(\d+)[\w\s]+(\d+)')
        result = reg.match(message.decode(self.encoding))
        self.user_count(*result.groups())

    def __op_count(self, params):
        """
        Command 252 event handler
        :param params: nick, op_count
        """
        self.op_count(params[1].decode(self.encoding))

    def __logged_in(self):
        """
        Command 900 event handler
        """
        self.logged_in()

    def __end_motd(self):
        """
        Command 376 event handler
        """
        self.__join_chans(self.chans)

    def __namreply(self, params, message):
        """
        Command 353 event handler
        :param params: nickname, channel
        :param message: list of channel's clients
        """
        channel = params[2].decode(self.encoding)
        users = message.decode(self.encoding).split(' ')
        self.namreply(channel, users)

    def __welcome(self):
        """
        Command 001 event handler
        """
        self.__send_auth()

    def __join_chans(self, channels):
        if channels:
            self.send('JOIN %s' % ','.join(channels))


    def __nick(self, prefix, params):
        """
        Command NICK event handler
        :param prefix: old nickname
        :param params: new nickname
        """
        prefix = prefix.decode(self.encoding).split('!')[0]
        params = params[0].decode(self.encoding)
        self.nick_changed(prefix, params)

    def __quit(self, prefix):
        """
        Command QUIT event handler
        :param prefix: the user that quit
        """
        prefix = prefix.decode(self.encoding).split('!')[0]
        self.quit(prefix)

    def __kick(self, params):
        """
        Command KICK event handler
        :param params: Contains the channel and the kicked user.
        """
        channel = params[0].decode(self.encoding)
        kicked_user = params[1].decode(self.encoding)
        self.kick(channel, kicked_user)

    def send(self, data: str):
        """
        Write to stream
        :param data: String to send
        """
        if type(data) is str:
            data = data.encode(self.encoding)

        if type(data) is bytes:
            self.stream.write(data + b'\r\n')
        else:
            raise TypeError('Data must be bytes or string')

    def closed(self, data):
        """
        Connection closed event
        :param data: None
        """
        IOLoop.current().stop()

    def motd(self, message):
        """
        MOTD event
        :param message: Line of MOTD
        """
        pass

    def ping(self, server1, server2):
        """
        PING event
        :param server1: Originating server
        :param server2: Forwarding server
        """
        pass

    def notice(self, prefix, params, message):
        """
        Notice event
        :param prefix: Sender
        :param params: Parameter list
        :param message: Notice message
        :return
        """
        pass

    def privmsg(self, source, target, message):
        """
        PRIVMSG event
        :param source:
        :param target:
        :param message:
        :return
        """
        pass

    def user_parted(self, user, channel, message):
        """
        PARTED event
        :param user: Parting users nickname
        :param channel: Channel the user parted from
        :param message: Part message
        """
        pass

    def user_joined(self, user, channel):
        """
        JOIN event
        :param user: Joining users nickname
        :param channel: Channel the user parted from
        :return:
        """
        pass

    def logged_in(self):
        """
        Successful login event
        """

        pass

    def user_count(self, users, services, servers):
        """
        251 RPL_LUSERCLIENT event
        :param users: Number of users online
        :param services: Number of services
        :param servers: Number of servers
        """
        pass

    def op_count(self, ops):
        """
        252 RPL_LUSEROP event
        :param ops: Number of ops online
        """
        pass

    def channel_mode(self, source, channel, mode, target):
        """
        Channel MODE event
        :param source: User that caused the mode change
        :param channel: Channel the event is for
        :param mode: A list of modes that were changed. Starts with +/-
        :param target: The user or channel that had its mode changed
        :return:
        """
        pass

    def user_mode(self, source, target, mode):
        """
        User MODE event
        :param source: User that caused the change
        :param target: User that had it's mode changed
        :param mode: A list of modes that were changed. Starts with +/-
        """
        pass

    def namreply(self, channel, users):
        """
        Command 353 event handler
        :param channel: nickname, channel
        :param users: list of channel's clients
        """
        pass

    def welcome(self):
        """
        Command 001 event handler
        """
        pass

    def nick_changed(self, old_nick, new_nick):
        """
        Command NICK event handler
        :param old_nick: user's nickname before change
        :param new_nick: user's nickname after change
        """
        pass

    def quit(self, nickname):
        """
        Command QUIT event handler
        :param nickname:  quitter's nickname
        """
        pass

    def kick(self, channel, kicked_user):
        """
        COmmand KICK event handler
        :param channel: Channel that the user was kicked from
        :param kicked_user: The user that was kicked
        """
        pass
