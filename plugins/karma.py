from cipher.irc import Plugin, Events
from cipher.db import execute
from tornado import gen
from tormysql.cursor import CursorNotReadAllDataError


class Help(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        Events.privmsg += [self.add_karma, self.remove_karma,
                           self.list, self.clear, self.reset]

    @gen.coroutine
    def add_karma(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return

        if message.endswith('++'):
            if self.user_mode(source, target) in ['~', '&', '@', '%', '+']:
                user = message.split('+')[0]
                if user == source:
                    self.irc.send('PRIVMSG %s You cannot give karma to yourself.' % target)

                else:
                    if user in self.irc.users and target in self.irc.users[user]:
                        yield execute('INSERT INTO gazelle.bot_karma (Username, Karma) '
                                      'VALUES(%s, 1) ON DUPLICATE KEY '
                                      'UPDATE Karma = Karma + 1', user)
                        self.irc.send('PRIVMSG %s Karma added.' % target)
                    else:
                        self.irc.send('PRIVMSG %s Do not try to give karma '
                                      'to users who are not on this channel.' % target)

    @gen.coroutine
    def remove_karma(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return

        if message.endswith('--'):
            if self.user_mode(source, target) in ['~', '&', '@', '%', '+']:
                user = message.split('-')[0]
                if user == source:
                    self.irc.send('PRIVMSG %s You cannot remove karma from yourself.' % target)
                else:
                    if user in self.irc.users and target in self.irc.users[user]:
                        yield execute('INSERT INTO gazelle.bot_karma (Username, Karma) '
                                      'VALUES(%s, -1) ON DUPLICATE KEY '
                                      'UPDATE Karma = Karma - 1', user)
                        self.irc.send('PRIVMSG %s Karma removed.' % target)
                    else:
                        self.irc.send('PRIVMSG %s Do not try to remove karma '
                                      'from users who are not on this channel.' % target)

    @gen.coroutine
    def list(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return
        if message.lower().startswith('!karma'):
            if self.user_mode(source, target) in ['~', '&', '@', '%', '+']:
                msg = message.split(' ')
                if len(msg) > 1:
                    user = msg[1]
                else:
                    user = source
                karma = yield execute('SELECT Username,Karma FROM bot_karma WHERE Username = %s', user)
                if karma:
                    username, karma = karma[0][:2]
                    self.irc.send('PRIVMSG %s %s has %s karma.' % (target, username, karma))
                else:
                    self.irc.send('PRIVMSG %s User (%s) has not been given karma.' % (target, user))

    @gen.coroutine
    def clear(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return

        if message.lower() == '!clearkarma':
            if self.user_mode(source, target) in ['~', '&']:
                try:
                    yield execute('TRUNCATE TABLE bot_karma;ALTER TABLE bot_karma AUTO_INCREMENT = 1;')
                except CursorNotReadAllDataError:
                    pass
                self.irc.send('PRIVMSG %s Karma table cleared.' % target)
            else:
                self.irc.send('PRIVMSG %s %s, you are not allowed to use this command.' % (target, source))

    @gen.coroutine
    def reset(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return

        if message.lower().startswith('!reset'):
            if self.user_mode(source, target) in ['~', '&', '@']:
                user = message.split(' ')[1]
                try:
                    yield execute('UPDATE bot_karma SET Karma = 0 WHERE Username = %s;', user)

                except CursorNotReadAllDataError:
                    self.irc.send('PRIVMSG %s User is not in the database.')
            else:
                self.irc.send('PRIVMSG %s You are not allowed to use this command.' % target)
