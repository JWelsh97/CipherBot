import ssl
from plugins import plugins
from .event import Events
from .irc import IRC


class Bot(IRC):
    def __init__(self, host: str, port: int, nickname: list, password: str,
                 enable_ssl: bool=False, ssl_options: ssl.SSLContext=None,
                 encoding: str='utf-8'):
        super().__init__(host, port, nickname, password, enable_ssl, ssl_options, encoding)
        self.plugins = []
        self.__load_plugins()
        self.users = {}

    def motd(self, message):
        print(message)

    def ping(self, server1, server2):
        print('PONG %s' % server1)

    def notice(self, prefix, params, message):
        print('%s: %s' % (prefix, message))

    def privmsg(self, source, target, message):
        user = source.split('!')[0]
        print('%s | %s | %s' % (target, user, message))
        Events.privmsg.notify(user, target, message)

    def logged_in(self):
        print('Logged in!')

    def user_count(self, users, services, servers):
        print('There are %s users and %s services on %s servers' % (users, services, servers))

    def op_count(self, ops):
        print('%s operator(s) online' % ops)

    def user_parted(self, user, channel, message):
        del(self.users[user][channel])
        if self.users[user] == {}:
            del(self.users[user])

        print('%s left %s (%s)' % (user, channel, message))
        Events.part.notify(user, channel, message)

    def user_joined(self, user, channel):
        self.users[user] = {}
        self.users[user][channel] = ''

        print('%s joined %s' % (user, channel))
        Events.join.notify(user, channel)

    def channel_mode(self, source, channel, mode, target):
        if mode[0] == '-':
            for m in mode[1:]:
                self.users[target][channel] = self.users[target][channel].replace(m, '')
        else:
            self.users[target][channel] += mode[1:]
        print('Mode %s [%s %s] by %s' % (channel, ''.join(mode), target, source))

    def user_mode(self, source, target, mode):
        print('Mode [%s %s] by %s' % (''.join(mode), target, source))

    def namreply(self, channel, users):
        for user in users:
            mode = user[0] if user[0] in ['~', '&', '@', '%', '+'] else ''
            modes = {'~': 'qo',
                     '&': 'ao',
                     '@': 'o',
                     '%': 'h',
                     '+': 'v',
                     '': ''}
            user = user[1:] if mode else user
            if user not in self.users:
                self.users[user] = {}
            self.users[user][channel] = modes[mode]
        print('%s: %s' % (channel, ', '.join(users)))

    def __load_plugins(self):
        for name, plugin in plugins:
            self.plugins.append(plugin(self))
            print('Loaded Plugin: %s' % name)
