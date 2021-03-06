import ssl
from plugins import plugins
from .event import Events
from .irc import IRC
from cipher import db


class Bot(IRC):
    def __init__(self, host: str, port: int, nickname: list, password: str, channels: list, op_pass: str,
                 enable_ssl: bool=False, ssl_options: ssl.SSLContext=None,
                 encoding: str='utf-8', db_config=None):
        super().__init__(host, port, nickname, password, channels, op_pass, enable_ssl, ssl_options, encoding)
        if db_config:
            db.connect(db_config)
        self.plugins = []
        self.__load_plugins()
        self.users = {}

    def motd(self, message):
        print(message)

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
        self.__add_user(user, channel)
        print('%s joined %s' % (user, channel))
        Events.join.notify(user, channel)

    def channel_mode(self, source, channel, mode, target):
        self.__add_user(target, channel)
        if mode[0] == '-':
            for m in mode[1:]:
                self.users[target][channel] = self.users[target][channel].replace(m, '')
        else:
            self.users[target][channel] += mode[1:]
        Events.mode_change.notify(channel, "".join(mode), target)
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

    def nick_changed(self, old_nick, new_nick):
        self.users[new_nick] = self.users.pop(old_nick)

    def quit(self, user):
        del(self.users[user])
        print('User %s QUIT' % user)
        Events.quit.notify(user)

    def kick(self, channel, kicked_user):
        print('User %s kicked from %s' % (kicked_user, channel))

    def closed(self, data):
        db.disconnect()
        super().closed(data)

    def __add_user(self, user, channel):
        if user not in self.users:
            self.users[user] = {}

        if channel not in self.users[user]:
            self.users[user][channel] = ''

    def __load_plugins(self):
        for name, plugin in plugins:
            self.plugins.append(plugin(self))
            print('Loaded Plugin: %s' % name)
