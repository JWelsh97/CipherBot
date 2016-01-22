from irc import IRC
import ssl


class Bot(IRC):
    def __init__(self, host: str, port: int, nicks: list, pwd: str,
                 use_ssl: bool=False, ssl_options: ssl.SSLContext=None,
                 encoding: str='utf-8'):
        super().__init__(host, port, nicks, pwd, use_ssl, ssl_options, encoding)

    def motd(self, message):
        print(message)

    def ping(self, server1, server2):
        print('PONG %s' % server1)

    def notice(self, prefix, params, message):
        print('%s: %s' % (prefix, message))

    def privmsg(self, source, target, message):
        user = source.split('!')[0]
        print('%s | %s | %s' % (target, user, message))

    def logged_in(self):
        print('Logged in!')

    def user_count(self, users, services, servers):
        print('There are %s users and %s services on %s servers' % (users, services, servers))

    def op_count(self, ops):
        print('%s operator(s) online' % ops)
