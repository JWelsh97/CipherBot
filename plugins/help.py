from cipher.irc import Plugin, Events
from tornado import gen


class Help(Plugin):
    def __init__(self, irc):
        super().__init__(irc)
        self.nickname = self.irc.nicks[0]
        Events.privmsg += [self.next, self.done, self.idler, self.help, self.list]
        Events.join += self.on_join
        Events.part += self.on_part
        Events.quit += self.quit
        Events.mode_change += self.mode_change
        self.__wait_queue = []

    def next(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return
        if target == '#help':
            if self.user_mode(source, target) in ['~', '&', '@']:
                if message == '!next':
                    if self.__wait_queue:
                        data = 'MODE #help +v %s' % self.__wait_queue.pop(0)
                        self.irc.send(data)

    def done(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return
        if self.user_mode(source, target) in ['~', '&', '@']:
            if message.startswith('!done'):
                message = message.split(' ')
                if len(message) < 2:
                    return
                user = message[1]
                if user not in self.__wait_queue:
                    data = 'KICK #help %s %s' % (user, 'You have been dealt with, \
                           if you have any other queries visit #help again.')
                    self.irc.send(data)
                else:
                    return

    def idler(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return
        if self.user_mode(source, target) in ['~', '&', '@']:
            if message.startswith('!idler'):
                message = message.split(' ')
                if len(message) < 2:
                    return
                user = message[1]
                if user not in self.__wait_queue:
                    data = 'KICK #help %s %s' % (user, 'There is no idling in this channel, if and when \
                           you come back, be sure to join #help again')
                    self.irc.send(data)
                else:
                    return

    def help(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return
        if target == '#tgif':
            if message == '!help':
                data = 'SAJOIN %s #help' % source
                self.irc.send(data)
            elif message.startswith('!help'):
                if self.user_mode(source, target) in ['~', '&', '@', '%']:
                    message = message.split(' ')
                    if len(message) < 2:
                        return
                    user = message[1]
                    data = 'SAJOIN %s #help' % user
                    self.irc.send(data)
                else:
                    self.irc.send('PRIVMSG #tgif You do not have permission to use this command.')

    def list(self, source: str, target: str, message: str):
        if not target.startswith('#'):
            return
        if target == '#help' and message == '!list':
            if not self.user_mode(source, target) in ['~', '&', '@']:
                self.irc.send('PRIVMSG #help You do not have permission to use this command.')
                return

            if not self.__wait_queue:
                self.irc.send('PRIVMSG #help Nobody is waiting.')
                return
            else:
                data = ' '.join(['%s: %s' % (x + 1, y) for x, y in enumerate(self.__wait_queue)])
                self.irc.send('PRIVMSG #help %s' % data)

    @gen.coroutine
    def on_join(self, user, channel):
        if channel == '#help':
            if user != self.nickname:
                self.__wait_queue.append(user)
                yield gen.sleep(1)
                if user in self.__wait_queue:
                    self.send_notice(user, 'Please wait to be voiced, \
                                           then you will be seen to.')

    def on_part(self, user, channel, message):
        if channel == '#help':
            if user in self.__wait_queue:
                self.__wait_queue.remove(user)

    def quit(self, user):
        if user in self.__wait_queue:
            self.__wait_queue.remove(user)

    def mode_change(self, channel, mode, target):
        if channel == '#help':
            if target in self.__wait_queue:
                if mode in ['+qo', '+ao', '+o']:
                    self.__wait_queue.remove(target)
